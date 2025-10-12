"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { signIn, signOut, useSession } from "next-auth/react";
import {
  Code2,
  Github,
} from "lucide-react";
import { BACKEND_URL } from "@/config";

// Define proper TypeScript interfaces
interface GitHubAccount {
  login: string;
  id: number;
  avatar_url: string;
  type: string;
}

interface Installation {
  id: number;
  account: GitHubAccount;
  app_id: number;
  target_type: string;
}

interface RepoOwner {
  login: string;
  id: number;
  avatar_url: string;
}

interface Repository {
  id: number;
  name: string;
  full_name: string;
  owner: RepoOwner;
  private: boolean;
  html_url: string;
  description: string | null;
}

interface InstallationsResponse {
  installations: Installation[];
}

interface ReposResponse {
  repositories: Repository[];
}

export default function DashboardPage() {
  const { data: session } = useSession();
  const [scrollY, setScrollY] = useState(0);
  const [repos, setRepos] = useState<Repository[]>([]);
  const [installations, setInstallations] = useState<Installation[]>([]);
  const [hasInstallation, setHasInstallation] = useState(false);
  const router = useRouter();
  const APP_SLUG = "codedaddy-reviewer";

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  async function fetchInstallations() {
    try {
      const res = await fetch(`${BACKEND_URL}/installations`, {
        headers: { Authorization: `Bearer ${session?.accessToken}` },
      });
      const data: InstallationsResponse = await res.json();
      const installs = data.installations || [];
      setInstallations(installs);
      setHasInstallation(installs.length > 0);

      // Automatically fetch repos for the first installation
      if (installs.length > 0) {
        fetchRepos(installs[0].id);
      }
    } catch (err) {
      console.error("Error fetching installations", err);
    }
  }

  async function fetchRepos(installationId: number) {
    try {
      const res = await fetch(
        `${BACKEND_URL}/repos?installation_id=${installationId}`,
        {
          headers: { Authorization: `Bearer ${session?.accessToken}` },
        }
      );
      const data: ReposResponse = await res.json();
      setRepos(data.repositories || []);
    } catch (err) {
      console.error("Error fetching repos", err);
    }
  }

  // Run on mount only if logged in
  useEffect(() => {
    if (session?.accessToken) {
      fetchInstallations();
    }
  }, [session?.accessToken]);

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
        <div className="text-center p-6 bg-slate-900/50 backdrop-blur-md rounded-xl">
          <h1 className="text-3xl font-bold mb-4">Login to Code Daddy</h1>
          <button
            className="px-6 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg transition text-white font-semibold"
            onClick={() => signIn("github")}
          >
            Sign in with GitHub
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 bg-slate-950/80 backdrop-blur-lg border-b border-purple-500/20">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Code2 className="w-8 h-8 text-purple-400" />
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Code Daddy
            </span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="hover:text-purple-400 transition">
              Features
            </a>
            <a href="#pricing" className="hover:text-purple-400 transition">
              Pricing
            </a>
            <a href="#about" className="hover:text-purple-400 transition">
              About
            </a>
            <button className="px-6 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition flex items-center gap-2">
              <Github className="w-5 h-5" />
              Install App
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6 text-center">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
          Welcome, <span className="text-purple-400">{session.user?.name}</span>
        </h1>
        <p className="text-xl text-slate-300 mb-6">
          Manage your GitHub App installations and repositories here.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-10">
          <button
            className="px-6 py-3 bg-purple-600 hover:bg-purple-500 rounded-lg transition text-white font-semibold"
            onClick={() => signOut()}
          >
            Logout
          </button>

          {!hasInstallation && (
            <a
              href={`https://github.com/apps/${APP_SLUG}/installations/new`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg font-semibold text-white transition"
            >
              Install GitHub App
            </a>
          )}
        </div>

        {/* Installations + Repos */}
        {hasInstallation && (
          <>
            <div className="bg-slate-900/50 backdrop-blur-md rounded-xl p-6 max-w-4xl mx-auto mb-10">
              <h2 className="text-2xl font-bold mb-4">Your Installations</h2>
              <ul className="space-y-2">
                {installations.map((inst) => (
                  <li
                    key={inst.id}
                    className="flex justify-between items-center bg-slate-800/50 p-2 rounded"
                  >
                    <span>{inst.account.login}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-900/50 backdrop-blur-md rounded-xl p-6 max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold mb-4">Repositories</h2>
              <ul className="space-y-2">
                {repos.map((repo) => (
                  <li
                    key={repo.id}
                    className="bg-slate-800/50 p-2 rounded cursor-pointer hover:bg-slate-700 transition"
                    onClick={() =>
                      router.push(
                        `/repo/${repo.owner.login}/${repo.name}?installation_id=${installations[0]?.id}`
                      )
                    }
                  >
                    {repo.full_name}
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
      </section>
    </div>
  );
}