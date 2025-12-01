"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();
  
  useEffect(() => {
    router.replace("/login");
  }, [router]);
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950">
      <div className="text-center">
        {/* Google Chrome-style loading spinner with logo colors */}
        <div className="relative w-16 h-16 mx-auto mb-4">
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-red-500 via-yellow-500 to-green-500 animate-spin"></div>
          <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-blue-500 via-transparent to-transparent animate-spin" style={{ animationDirection: 'reverse' }}></div>
          <div className="absolute inset-2 rounded-full bg-slate-950"></div>
        </div>
        <p className="text-slate-400">Redirecting...</p>
      </div>
    </div>
  );
}
