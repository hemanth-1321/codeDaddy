"use client";
import { useState, useEffect } from "react";
import { Moon } from "lucide-react";
import { signIn, signOut, useSession } from "next-auth/react";
import ThemeToggle from "./ThemeToggle";
export default function Appbar() {
  const { data: session } = useSession();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 transition-all duration-300 w-full max-w-5xl px-4 ${
        scrolled ? "top-2" : ""
      }`}
    >
      <div
        className={`transition-all duration-300 rounded-full px-6 ${
          scrolled
            ? "dark:bg-[#191919] bg-gray-300 backdrop-blur-sm shadow-lg"
            : "bg-transparent"
        }`}
      >
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-6 h-6 dark:bg-white bg-black rounded"></div>
            <span className=" font-medium text-sm">Code_Daddy</span>
          </div>

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            <ThemeToggle/>
            {session ? (
              // If user is logged in
              <button
                onClick={() => signOut()}
                className="transition-colors text-sm hidden md:block"
              >
                Logout
              </button>
            ) : (
              // If user is not logged in
              <button
                onClick={() => signIn("github")}
                className=" transition-colors text-sm hidden md:block"
              >
                Login
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
