import { PrismaClient } from "@prisma/client";

declare global {
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined;
}

// Configure Prisma with proper connection pooling
const prismaOptions: ConstructorParameters<typeof PrismaClient>[0] = {
  log: process.env.NODE_ENV === "development" ? ["query", "warn", "error"] : ["error"],
  // Optimize connection pool
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
  // Connection pool configuration
  // These are handled via DATABASE_URL parameters or connection pooling service
};

// Use connection pooling URL if available, otherwise use regular DATABASE_URL
// Connection pooling URL format: postgresql://user:password@host:port/database?pgbouncer=true&connection_limit=1
const databaseUrl = process.env.DATABASE_URL;

export const prisma =
  global.prisma ??
  new PrismaClient({
    ...prismaOptions,
    datasources: databaseUrl ? {
      db: {
        url: databaseUrl,
      },
    } : undefined,
  });

if (process.env.NODE_ENV !== "production") {
  global.prisma = prisma;
}

// Gracefully disconnect on process termination (server-side only)
if (typeof window === "undefined") {
  const shutdown = async () => {
    try {
      await prisma.$disconnect();
    } catch (error) {
      console.error("Error disconnecting Prisma:", error);
    }
  };
  
  if (process.env.NODE_ENV === "production") {
    // In production, handle cleanup on process exit
    process.on("beforeExit", shutdown);
    process.on("SIGINT", shutdown);
    process.on("SIGTERM", shutdown);
  }
}


