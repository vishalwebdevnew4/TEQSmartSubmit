"""Local CAPTCHA solver implementation without third-party dependencies."""

import os
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import re
import logging
from typing import Optional, Dict, Any, List, Tuple
import io
import base64

logger = logging.getLogger(__name__)

class LocalCaptchaSolver:
    """Local CAPTCHA solver using image processing and OCR."""
    
    def __init__(self, tesseract_path: str = None):
        """
        Initialize the CAPTCHA solver.
        
        Args:
            tesseract_path: Optional path to tesseract executable
        """
        self.tesseract_path = tesseract_path
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Common CAPTCHA patterns
        self.captcha_patterns = [
            r'[A-Z0-9]{4,8}',  # Uppercase alphanumeric (4-8 chars)
            r'[a-zA-Z0-9]{4,6}',  # Mixed case alphanumeric
            r'\d{4,6}',  # Numbers only
            r'[A-Z]{4,6}',  # Uppercase letters only
        ]
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess CAPTCHA image for better OCR results."""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.MedianFilter(3))
            
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Apply threshold to binarize
            _, thresh = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Remove noise using morphological operations
            kernel = np.ones((2, 2), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Convert back to PIL Image
            image = Image.fromarray(thresh)
            
            return image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from CAPTCHA image using Tesseract."""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Configure Tesseract for CAPTCHA
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            
            # Try with different configurations
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            text = text.strip()
            
            # If no result, try with different page segmentation mode
            if not text:
                custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                text = pytesseract.image_to_string(processed_image, config=custom_config)
                text = text.strip()
            
            # Clean up the text
            text = re.sub(r'[^A-Za-z0-9]', '', text)
            
            return text
            
        except Exception as e:
            logger.warning(f"OCR extraction failed: {e}")
            return ""
    
    def validate_captcha_text(self, text: str) -> bool:
        """Validate if extracted text looks like a valid CAPTCHA."""
        if not text or len(text) < 3 or len(text) > 8:
            return False
        
        # Check against common CAPTCHA patterns
        for pattern in self.captcha_patterns:
            if re.fullmatch(pattern, text):
                return True
        
        # Additional validation - should contain only alphanumeric characters
        if not re.match(r'^[A-Za-z0-9]+$', text):
            return False
        
        return True
    
    def solve_captcha_image(self, image: Image.Image, max_attempts: int = 3) -> Optional[str]:
        """Solve CAPTCHA from image with multiple attempts."""
        for attempt in range(max_attempts):
            try:
                # Apply different preprocessing for each attempt
                if attempt == 1:
                    # Brighten image
                    enhancer = ImageEnhance.Brightness(image)
                    test_image = enhancer.enhance(1.5)
                elif attempt == 2:
                    # Increase contrast more
                    test_image = self.preprocess_image(image)
                    enhancer = ImageEnhance.Contrast(test_image)
                    test_image = enhancer.enhance(3.0)
                else:
                    test_image = self.preprocess_image(image)
                
                text = self.extract_text_from_image(test_image)
                
                if self.validate_captcha_text(text):
                    logger.info(f"CAPTCHA solved: {text} (attempt {attempt + 1})")
                    return text
                    
            except Exception as e:
                logger.warning(f"CAPTCHA solving attempt {attempt + 1} failed: {e}")
                continue
        
        return None
    
    def solve_captcha_from_base64(self, base64_string: str) -> Optional[str]:
        """Solve CAPTCHA from base64 encoded image."""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',', 1)[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
            
            return self.solve_captcha_image(image)
            
        except Exception as e:
            logger.warning(f"Base64 CAPTCHA solving failed: {e}")
            return None
    
    async def solve_captcha_from_url(self, page, img_selector: str) -> Optional[str]:
        """Solve CAPTCHA by extracting image from page."""
        try:
            # Get image source
            img_src = await page.evaluate(f"""
            () => {{
                const img = document.querySelector('{img_selector}');
                return img ? img.src : null;
            }}
            """)
            
            if not img_src:
                return None
            
            if img_src.startswith('data:image'):
                return self.solve_captcha_from_base64(img_src)
            else:
                # Download image (for non-data URLs)
                logger.warning("External image URLs require download implementation")
                return None
                
        except Exception as e:
            logger.warning(f"URL CAPTCHA solving failed: {e}")
            return None


class AudioCaptchaSolver:
    """Simple audio CAPTCHA solver (basic implementation)."""
    
    def __init__(self):
        self.number_words = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'
        }
    
    def solve_audio_captcha(self, audio_data: bytes) -> Optional[str]:
        """Basic audio CAPTCHA solver (placeholder implementation)."""
        # Note: Proper audio CAPTCHA solving requires speech recognition libraries
        # This is a simplified version that would need enhancement
        logger.warning("Audio CAPTCHA solving requires additional implementation")
        return None


class MathematicalCaptchaSolver:
    """Solver for mathematical CAPTCHAs (e.g., '2 + 3 = ?')."""
    
    def solve_math_captcha(self, text: str) -> Optional[str]:
        """Solve mathematical CAPTCHA."""
        try:
            # Remove spaces and make lowercase
            text = text.lower().replace(' ', '')
            
            # Common math CAPTCHA patterns
            patterns = [
                r'(\d+)[\+](\d+)',  # Addition
                r'(\d+)[\-](\d+)',  # Subtraction  
                r'(\d+)[\*](\d+)',  # Multiplication
                r'(\d+)[\/](\d+)',  # Division
                r'whatis(\d+)[\+](\d+)',
                r'whatis(\d+)[\-](\d+)',
                r'(\d+)plus(\d+)',
                r'(\d+)minus(\d+)',
                r'(\d+)times(\d+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    num1 = int(match.group(1))
                    num2 = int(match.group(2))
                    
                    if '+' in text or 'plus' in text:
                        return str(num1 + num2)
                    elif '-' in text or 'minus' in text:
                        return str(num1 - num2)
                    elif '*' in text or 'times' in text:
                        return str(num1 * num2)
                    elif '/' in text:
                        return str(num1 // num2) if num2 != 0 else '0'
            
            return None
            
        except Exception as e:
            logger.warning(f"Math CAPTCHA solving failed: {e}")
            return None


class UniversalCaptchaSolver:
    """Universal CAPTCHA solver that combines multiple approaches."""
    
    def __init__(self, tesseract_path: str = None):
        self.image_solver = LocalCaptchaSolver(tesseract_path)
        self.audio_solver = AudioCaptchaSolver()
        self.math_solver = MathematicalCaptchaSolver()
        
        # CAPTCHA detection patterns
        self.captcha_indicators = [
            'captcha', 'recaptcha', 'security code', 'verification code',
            'human verification', 'anti-spam', 'type the text', 'enter the text'
        ]
    
    async def detect_captcha_fields(self, page) -> List[Dict[str, Any]]:
        """Detect CAPTCHA-related fields on the page."""
        try:
            captcha_elements = await page.evaluate("""
            () => {
                const elements = [];
                
                // Find CAPTCHA images
                const captchaImages = Array.from(document.querySelectorAll('img')).filter(img => {
                    const src = img.src.toLowerCase();
                    const alt = img.alt.toLowerCase();
                    const parentText = img.parentElement?.textContent.toLowerCase() || '';
                    
                    return src.includes('captcha') || alt.includes('captcha') || 
                           parentText.includes('captcha') || parentText.includes('security code') ||
                           src.includes('securo') || alt.includes('verification');
                });
                
                captchaImages.forEach(img => {
                    elements.push({
                        type: 'image_captcha',
                        selector: 'img[src*="captcha"], img[alt*="captcha"]',
                        element: img
                    });
                });
                
                // Find CAPTCHA input fields
                const inputs = Array.from(document.querySelectorAll('input'));
                const captchaInputs = inputs.filter(input => {
                    const name = input.name.toLowerCase();
                    const id = input.id.toLowerCase();
                    const placeholder = input.placeholder.toLowerCase();
                    const type = input.type.toLowerCase();
                    
                    return name.includes('captcha') || id.includes('captcha') || 
                           placeholder.includes('captcha') || placeholder.includes('security code') ||
                           name.includes('verification') || id.includes('verif') ||
                           placeholder.includes('enter text') || placeholder.includes('type the');
                });
                
                captchaInputs.forEach(input => {
                    elements.push({
                        type: 'captcha_input',
                        selector: `input[name="${input.name}"], input[id="${input.id}"]`,
                        element: input
                    });
                });
                
                // Find reCAPTCHA elements
                const recaptchaElements = Array.from(document.querySelectorAll('.g-recaptcha, .recaptcha, iframe[src*="google.com/recaptcha"]'));
                recaptchaElements.forEach(el => {
                    elements.push({
                        type: 'recaptcha',
                        selector: '.g-recaptcha, .recaptcha, iframe[src*="recaptcha"]',
                        element: el
                    });
                });
                
                return elements.map(el => ({
                    type: el.type,
                    selector: el.selector
                }));
            }
            """)
            
            return captcha_elements or []
            
        except Exception as e:
            logger.warning(f"CAPTCHA detection failed: {e}")
            return []
    
    async def solve_captcha(self, page, captcha_element: Dict[str, Any]) -> Optional[str]:
        """Solve CAPTCHA based on element type."""
        try:
            captcha_type = captcha_element.get('type', '')
            selector = captcha_element.get('selector', '')
            
            if captcha_type == 'image_captcha':
                return await self.image_solver.solve_captcha_from_url(page, selector)
            
            elif captcha_type == 'captcha_input':
                # For text-based CAPTCHAs, we need to find the associated image
                # Look for nearby images that might be the CAPTCHA
                nearby_image = await page.evaluate(f"""
                () => {{
                    const input = document.querySelector('{selector}');
                    if (!input) return null;
                    
                    // Look for images near the input
                    const parent = input.parentElement;
                    const images = parent ? Array.from(parent.querySelectorAll('img')) : [];
                    
                    if (images.length > 0) return images[0].src;
                    
                    // Look in previous siblings
                    let prev = input.previousElementSibling;
                    while (prev) {{
                        if (prev.tagName === 'IMG') return prev.src;
                        prev = prev.previousElementSibling;
                    }}
                    
                    return null;
                }}
                """)
                
                if nearby_image and nearby_image.startswith('data:image'):
                    return self.image_solver.solve_captcha_from_base64(nearby_image)
            
            elif captcha_type == 'recaptcha':
                logger.warning("reCAPTCHA requires manual intervention or advanced solving")
                return None
            
            return None
            
        except Exception as e:
            logger.warning(f"CAPTCHA solving failed: {e}")
            return None
    
    def bypass_simple_captcha(self, page) -> bool:
        """Attempt to bypass simple CAPTCHA implementations."""
        try:
            # Look for hidden CAPTCHA fields that might be bypassed
            hidden_captcha = page.evaluate("""
            () => {
                // Look for honeypot CAPTCHA fields
                const inputs = Array.from(document.querySelectorAll('input'));
                const honeypot = inputs.find(input => {
                    const style = window.getComputedStyle(input);
                    return style.display === 'none' || 
                           style.visibility === 'hidden' ||
                           input.offsetParent === null ||
                           input.type === 'hidden' ||
                           input.hasAttribute('data-captcha');
                });
                
                return honeypot ? honeypot.name : null;
            }
            """)
            
            if hidden_captcha:
                logger.info(f"Found potential honeypot CAPTCHA field: {hidden_captcha}")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Simple CAPTCHA bypass failed: {e}")
            return False


# Utility functions for CAPTCHA handling
async def handle_captcha_in_form(page, form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Automatically handle CAPTCHA in forms if possible."""
    solver = UniversalCaptchaSolver()
    
    # Detect CAPTCHA elements
    captcha_elements = await solver.detect_captcha_fields(page)
    
    if not captcha_elements:
        logger.info("No CAPTCHA detected in form")
        return form_data
    
    logger.info(f"Detected {len(captcha_elements)} CAPTCHA elements")
    
    solved_captcha = None
    
    for captcha_element in captcha_elements:
        # Try to solve the CAPTCHA
        solution = await solver.solve_captcha(page, captcha_element)
        
        if solution:
            solved_captcha = solution
            logger.info(f"Successfully solved CAPTCHA: {solution}")
            break
    
    # If CAPTCHA was solved, add it to form data
    if solved_captcha:
        # Find the CAPTCHA input field
        captcha_input = page.evaluate("""
        () => {
            const inputs = Array.from(document.querySelectorAll('input'));
            const captchaInput = inputs.find(input => {
                const name = input.name.toLowerCase();
                const id = input.id.toLowerCase();
                const placeholder = input.placeholder.toLowerCase();
                
                return name.includes('captcha') || id.includes('captcha') || 
                       placeholder.includes('captcha') || placeholder.includes('security code') ||
                       name.includes('verification') || id.includes('verif');
            });
            
            return captchaInput ? captchaInput.name : null;
        }
        """)
        
        if captcha_input:
            form_data['fields'].append({
                'name': captcha_input,
                'selector': f'input[name="{captcha_input}"]',
                'value': solved_captcha,
                'captcha_solved': True
            })
    
    # Try to bypass simple CAPTCHA implementations
    if not solved_captcha:
        if solver.bypass_simple_captcha(page):
            logger.info("Successfully bypassed simple CAPTCHA")
    
    return form_data


async def wait_for_captcha_manual_fallback(page, timeout: int = 120) -> bool:
    """Wait for manual CAPTCHA solving with fallback."""
    logger.warning("CAPTCHA detected requiring manual intervention")
    
    try:
        # Wait for user to solve CAPTCHA manually
        await page.wait_for_function(
            """
            () => {
                // Check if CAPTCHA input has been filled
                const inputs = Array.from(document.querySelectorAll('input'));
                const captchaInput = inputs.find(input => {
                    const name = input.name.toLowerCase();
                    return name.includes('captcha') || name.includes('verification');
                });
                
                return captchaInput && captchaInput.value.length > 0;
            }
            """,
            timeout=timeout * 1000
        )
        
        logger.info("CAPTCHA appears to have been solved manually")
        return True
        
    except Exception as e:
        logger.warning(f"Manual CAPTCHA solving timeout or error: {e}")
        return False


# Installation helper functions
def check_tesseract_installation() -> bool:
    """Check if Tesseract is installed and accessible."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False

def get_installation_instructions() -> str:
    """Get installation instructions for dependencies."""
    instructions = """
CAPTCHA Solver Dependencies Installation:
    
1. Install Tesseract OCR:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - macOS: brew install tesseract
   - Linux: sudo apt-get install tesseract-ocr

2. Install Python packages:
   pip install pytesseract opencv-python pillow numpy

3. Set Tesseract path if not in system PATH:
   solver = LocalCaptchaSolver(tesseract_path='/path/to/tesseract')
    """
    return instructions