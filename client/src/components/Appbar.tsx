"use client";

import { useState, useEffect } from "react";
import { signIn, signOut, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Menu, X } from "lucide-react"; 
import ThemeToggle from "./ThemeToggle";

export default function Appbar() {
  const { data: session } = useSession();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
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
          <div
            onClick={() => router.push("/")}
            className="text-xl font-extrabold bg-gradient-to-r from-orange-500 to-red-400 bg-clip-text text-transparent 
              tracking-tight hover:opacity-90 transition-opacity duration-200 cursor-pointer select-none"
          >
            Code-Daddy
          </div>

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            <ThemeToggle />

            {/* Desktop Login/Logout */}
            {session ? (
              <button
                onClick={() => signOut()}
                className="transition-colors text-sm hidden md:block cursor-pointer"
              >
                Logout
              </button>
            ) : (
              <button
                onClick={() => signIn("github")}
                className="transition-colors text-sm hidden md:block cursor-pointer"
              >
                Login
              </button>
            )}

            {/* Mobile Hamburger */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden p-2 rounded-full hover:bg-gray-200 dark:hover:bg-[#2a2a2a]"
            >
              {menuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {menuOpen && (
          <div className="md:hidden mt-2 py-3 px-4 rounded-2xl dark:bg-[#191919] bg-gray-200 shadow-md flex flex-col space-y-2">
            {session ? (
              <button
                onClick={() => {
                  signOut();
                  setMenuOpen(false);
                }}
                className="text-sm text-left w-full"
              >
                Logout
              </button>
            ) : (
              <button
                onClick={() => {
                  signIn("github");
                  setMenuOpen(false);
                }}
                className="text-sm text-left w-full"
              >
                Login
              </button>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
