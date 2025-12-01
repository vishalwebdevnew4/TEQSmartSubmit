// Create admin user using Prisma (for Next.js database)
const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

async function createAdmin() {
  const username = process.argv[2] || 'admin';
  const password = process.argv[3] || 'admin123';
  
  try {
    // Check if user exists
    const existing = await prisma.admin.findUnique({
      where: { username }
    });
    
    if (existing) {
      console.log(`[ERROR] User '${username}' already exists`);
      process.exit(1);
    }
    
    // Hash password
    const passwordHash = await bcrypt.hash(password, 12);
    
    // Create admin
    const admin = await prisma.admin.create({
      data: {
        username,
        passwordHash,
        role: 'admin',
        isActive: true,
      }
    });
    
    console.log(`\n[OK] Admin user '${username}' created successfully!`);
    console.log(`   Role: admin`);
    console.log(`\nYou can now login with:`);
    console.log(`   Username: ${username}`);
    console.log(`   Password: ${password}`);
    
  } catch (error) {
    console.error('[ERROR] Error creating admin:', error.message);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

createAdmin();

