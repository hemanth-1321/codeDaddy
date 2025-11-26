"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import {
  Search,
  Plus,
  Github,
  Lock,
  Unlock,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Loader2,
} from "lucide-react";
import { BACKEND_URL } from "@/config";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

interface GitHubAccount {
  login: string;
  id: number;
  avatar_url: string;
  type: string;
}

interface Repo {
  id: number;
  name: string;
  full_name: string;
  html_url: string;
  private: boolean;
}

interface Installation {
  id: number;
  account: GitHubAccount;
  app_id: number;
  target_type: string;
  repos?: Repo[];
}

interface InstallationsResponse {
  username: string;
  installations: Installation[];
}

export default function Page() {
  const { data: session } = useSession();
  const [installations, setInstallations] = useState<Installation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const router = useRouter();
  const APP_SLUG = "codedaddy-reviewer";

  const allRepos = installations.flatMap((inst) => inst.repos || []);

  const filteredRepos = allRepos.filter((repo) =>
    repo.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalPages = Math.ceil(filteredRepos.length / rowsPerPage);
  const startIndex = (currentPage - 1) * rowsPerPage;
  const paginatedRepos = filteredRepos.slice(
    startIndex,
    startIndex + rowsPerPage
  );

  const fetchInstallations = async () => {
    if (!session?.user?.login) return;

    try {
      const res = await axios.get<InstallationsResponse>(
        `${BACKEND_URL}/installations?username=${session.user.login}`
      );

      const installs = res.data.installations;
      setInstallations(installs);

      for (const inst of installs) {
        await fetchRepos(inst.id);
      }

      setLoading(false);
    } catch (err) {
      console.error("Error fetching installations:", err);
      setLoading(false);
    }
  };

  const fetchRepos = async (installationId: number) => {
    try {
      const res = await axios.get(
        `${BACKEND_URL}/repos?installation_id=${installationId}`
      );
      const repos = res.data.repositories || res.data.repos || [];

      setInstallations((prev) =>
        prev.map((inst) =>
          inst.id === installationId ? { ...inst, repos } : inst
        )
      );
    } catch (err) {
      console.error(
        `Error fetching repos for installation ${installationId}:`,
        err
      );
    }
  };

  useEffect(() => {
    if (session) {
      fetchInstallations();
    }
  }, [session]);

  if (!session) {
    router.push("/");
    return null;
  }

  // Loading State - Redesigned to match new UI
  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white pt-20 pb-12">
        <div className="px-4 sm:px-6 max-w-5xl mx-auto space-y-8">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
            <div className="space-y-2">
              <Skeleton className="h-8 w-48 bg-zinc-800 rounded-md" />
              <Skeleton className="h-4 w-64 bg-zinc-800 rounded-md" />
            </div>
            <Skeleton className="h-10 w-32 bg-zinc-800 rounded-lg" />
          </div>

          <div className="space-y-4">
            <Skeleton className="h-12 w-full bg-zinc-800 rounded-xl" />
            {[...Array(5)].map((_, i) => (
              <Skeleton
                key={i}
                className="h-20 w-full bg-zinc-900 border border-zinc-800 rounded-xl"
              />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-zinc-100 mt-15 selection:bg-orange-500/30">
      <div className="pt-8 px-4 sm:px-6 pb-12 max-w-5xl mx-auto">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight text-white">
              Repositories
            </h1>
            <p className="text-zinc-400">
              Manage the repositories connected to CodeRabbit.
            </p>
          </div>

          <Button
            onClick={() => {
              window.open(
                `https://github.com/apps/${APP_SLUG}/installations/new`,
                "_blank"
              );
            }}
            className="group relative inline-flex items-center justify-center gap-2 px-6 py-2.5 bg-[#ff6b35] hover:bg-[#ff8f65] text-white font-medium rounded-full transition-all duration-200 shadow-[0_0_20px_-5px_rgba(255,107,53,0.5)] hover:shadow-[0_0_25px_-5px_rgba(255,107,53,0.6)]"
          >
            <Plus className="w-5 h-5 transition-transform group-hover:rotate-90" />
            <span>Add Repositories</span>
          </Button>
        </div>

        {/* Search & Filter Section */}
        <div className="mb-6 relative group">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-zinc-500 group-focus-within:text-[#ff6b35] transition-colors" />
          </div>
          <input
            type="text"
            placeholder="Search repositories..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            className="block w-full pl-10 pr-4 py-3 bg-zinc-900/50 border border-zinc-800 rounded-xl text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-[#ff6b35]/50 focus:border-[#ff6b35] transition-all duration-200"
          />
        </div>

        {/* Stats Bar */}
        <div className="flex items-center justify-between text-xs sm:text-sm text-zinc-500 mb-4 px-1">
          <span>
            Showing {paginatedRepos.length} of {filteredRepos.length}{" "}
            repositories
          </span>
          {loading && <Loader2 className="w-4 h-4 animate-spin" />}
        </div>

        {/* Repository List */}
        <div className="space-y-3">
          {paginatedRepos.length > 0 ? (
            paginatedRepos.map((repo) => (
              <div
                key={repo.id}
                onClick={() => window.open(repo.html_url, "_blank")}
                className="group relative flex flex-col sm:flex-row sm:items-center justify-between p-4 sm:p-5 bg-zinc-900/40 hover:bg-zinc-900 border border-zinc-800 hover:border-zinc-700 rounded-xl transition-all duration-200 cursor-pointer overflow-hidden"
              >
                {/* Hover Glow Effect */}
                <div className="absolute inset-y-0 left-0 w-1 bg-[#ff6b35] opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

                <div className="flex items-start sm:items-center gap-4 mb-2 sm:mb-0">
                  <div className="p-2 bg-zinc-800 rounded-lg group-hover:bg-zinc-800/80 transition-colors">
                    <Github className="w-6 h-6 text-zinc-100" />
                  </div>

                  <div className="flex flex-col">
                    <span className="text-base sm:text-lg font-semibold text-zinc-100 group-hover:text-[#ff6b35] transition-colors break-all">
                      {repo.name}
                    </span>
                    <span className="text-sm text-zinc-500 font-mono hidden sm:block">
                      {repo.full_name}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-4 mt-2 sm:mt-0 pl-12 sm:pl-0">
                  <span
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${
                      repo.private
                        ? "bg-zinc-800/50 border-zinc-700 text-zinc-400"
                        : "bg-emerald-950/30 border-emerald-900/50 text-emerald-500"
                    }`}
                  >
                    {repo.private ? (
                      <Lock className="w-3 h-3" />
                    ) : (
                      <Unlock className="w-3 h-3" />
                    )}
                    {repo.private ? "Private" : "Public"}
                  </span>

                  <ExternalLink className="w-5 h-5 text-zinc-600 group-hover:text-zinc-300 opacity-0 group-hover:opacity-100 transition-all duration-200 transform translate-x-2 group-hover:translate-x-0 hidden sm:block" />
                </div>
              </div>
            ))
          ) : (
            <div className="flex flex-col items-center justify-center py-16 px-4 bg-zinc-900/20 border border-dashed border-zinc-800 rounded-xl text-center">
              <div className="bg-zinc-900 p-4 rounded-full mb-4">
                <Github className="w-8 h-8 text-zinc-500" />
              </div>
              <h3 className="text-lg font-medium text-zinc-200 mb-1">
                {searchQuery
                  ? "No matching repositories"
                  : "No repositories found"}
              </h3>
              <p className="text-zinc-500 max-w-sm">
                {searchQuery
                  ? "Try adjusting your search terms to find what you're looking for."
                  : "It looks like you haven't installed the GitHub App yet."}
              </p>
            </div>
          )}
        </div>

        {/* Pagination */}
        {filteredRepos.length > 0 && (
          <div className="mt-8 flex flex-col-reverse sm:flex-row items-center justify-between gap-6 border-t border-zinc-800 pt-6">
            <div className="flex items-center gap-3">
              <span className="text-sm text-zinc-500">Rows per page:</span>
              <select
                value={rowsPerPage}
                onChange={(e) => {
                  setRowsPerPage(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="bg-zinc-900 border border-zinc-800 rounded-md px-2 py-1 text-sm text-zinc-300 focus:outline-none focus:ring-1 focus:ring-[#ff6b35] cursor-pointer"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>

            <div className="flex items-center gap-1">
              <span className="text-sm text-zinc-500 mr-4">
                Page{" "}
                <span className="text-zinc-200 font-medium">{currentPage}</span>{" "}
                of {totalPages}
              </span>

              <div className="flex gap-1 bg-zinc-900/50 p-1 rounded-lg border border-zinc-800">
                <button
                  onClick={() => setCurrentPage(1)}
                  disabled={currentPage === 1}
                  className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-md disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                  aria-label="First page"
                >
                  <ChevronsLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() =>
                    setCurrentPage((prev) => Math.max(1, prev - 1))
                  }
                  disabled={currentPage === 1}
                  className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-md disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                  aria-label="Previous page"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() =>
                    setCurrentPage((prev) => Math.min(totalPages, prev + 1))
                  }
                  disabled={currentPage === totalPages}
                  className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-md disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                  aria-label="Next page"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={currentPage === totalPages}
                  className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-md disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                  aria-label="Last page"
                >
                  <ChevronsRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
