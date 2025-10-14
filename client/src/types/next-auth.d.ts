import "next-auth";
import "next-auth/jwt";

declare module "next-auth" {
  interface Session {
    user: {
      id: string;
      jwtToken: string;
      role: string;
      avatarUrl?: string;
      email: string;
      name: string;
      login: string;
    };
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    uid?: string;
    username?: string;
    avatarUrl?: string;
    accessToken?: string;
    role?: string;
    email?: string;
    name?: string;
  }
}
