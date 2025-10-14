"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { Search, Plus } from "lucide-react";
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
  const paginatedRepos = filteredRepos.slice(startIndex, startIndex + rowsPerPage);

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
      const res = await axios.get(`${BACKEND_URL}/repos?installation_id=${installationId}`);
      const repos = res.data.repositories || res.data.repos || [];

      setInstallations((prev) =>
        prev.map((inst) =>
          inst.id === installationId ? { ...inst, repos } : inst
        )
      );
    } catch (err) {
      console.error(`Error fetching repos for installation ${installationId}:`, err);
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

  if (loading) {
    return (
      <div className="min-h-screen mt-15">
        <div className="pt-4 sm:pt-8 px-4 sm:px-6 pb-12 max-w-7xl mx-auto">
          {/* Header Skeleton */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-6">
            <div className="flex-1">
              <Skeleton className="h-8 sm:h-9 w-48 mb-2" />
              <Skeleton className="h-4 sm:h-5 w-full sm:w-96" />
            </div>
            <Skeleton className="h-10 w-full sm:w-44" />
          </div>

          {/* Search Bar Skeleton */}
          <div className="mb-6">
            <Skeleton className="h-10 w-full sm:max-w-md" />
          </div>

          {/* Table Container */}
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg overflow-hidden">
            {/* Table Header - Hidden on mobile */}
            <div className="hidden sm:block border-b border-[#30363d] px-6 py-3 bg-[#0d1117]">
              <Skeleton className="h-5 w-32" />
            </div>

            {/* Table Body Skeletons */}
            <div className="divide-y divide-[#30363d]">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="px-4 sm:px-6 py-3 sm:py-4">
                  <div className="flex items-center gap-2 sm:gap-3">
                    <Skeleton className="h-5 w-32 sm:w-48" />
                    <Skeleton className="h-5 w-14 sm:w-16" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen mt-15">
      <div className="pt-4 sm:pt-8 px-4 sm:px-6 pb-12 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 mb-6">
          <div className="flex-1">
            <h1 className="text-2xl sm:text-3xl font-semibold mb-2">Repositories</h1>
            <p className="text-sm sm:text-base text-gray-400">
              List of repositories accessible to CodeRabbit.
            </p>
          </div>
          <Button
            onClick={() => {
              window.open(`https://github.com/apps/${APP_SLUG}/installations/new`, "_blank");
            }}
            className="w-full sm:w-auto px-4 py-2 bg-[#ff6b35] hover:bg-[#ff7f50] rounded-lg transition text-white font-medium flex items-center justify-center gap-2"
          >
            <Plus className="w-5 h-5" />
            <span className="sm:inline">Add Repositories</span>
          </Button>

        </div>

        {/* Search Bar */}
        <div className="mb-6 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Repo not found? Search here..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full sm:max-w-md bg-[#161b22] border border-[#30363d] rounded-lg py-2.5 pl-10 pr-4 text-sm sm:text-base text-gray-300 placeholder-gray-500 focus:outline-none focus:border-[#ff6b35] transition"
          />
        </div>

        {/* Table Container */}
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg overflow-hidden">
          {/* Table Header - Hidden on mobile */}
          <div className="hidden sm:block border-b border-[#30363d] px-6 py-3 bg-[#0d1117]">
            <div className="flex items-center gap-2">
              <span className="text-gray-400 font-medium">Repository</span>
              <svg
                className="w-4 h-4 text-gray-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
                />
              </svg>
            </div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-[#30363d]">
            {paginatedRepos.length > 0 ? (
              paginatedRepos.map((repo) => (
                <div
                  key={repo.id}
                  className="px-4 sm:px-6 py-3 sm:py-4 hover:bg-[#1c2128] transition cursor-pointer"
                  onClick={() => window.open(repo.html_url, "_blank")}
                >
                  <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
                    <span className="text-sm sm:text-base text-gray-200 font-medium break-all">
                      {repo.name}
                    </span>
                    <span className="px-2 py-0.5 bg-[#21262d] border border-[#30363d] rounded text-xs text-gray-400 whitespace-nowrap">
                      {repo.private ? "Private" : "Public"}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-4 sm:px-6 py-8 sm:py-12 text-center text-sm sm:text-base text-gray-500">
                {searchQuery
                  ? "No repositories found matching your search."
                  : "No repositories found. Please install the GitHub App first."}
              </div>
            )}
          </div>
        </div>

        {/* Pagination */}
        {filteredRepos.length > 0 && (
          <div className="mt-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3 sm:gap-4">
              <span className="text-gray-400 text-xs sm:text-sm whitespace-nowrap">
                Rows per page
              </span>
              <select
                value={rowsPerPage}
                onChange={(e) => {
                  setRowsPerPage(Number(e.target.value));
                  setCurrentPage(1);
                }}
                className="bg-[#161b22] border border-[#30363d] rounded-lg px-2 sm:px-3 py-1.5 text-sm text-gray-300 focus:outline-none focus:border-[#ff6b35] cursor-pointer"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>

            <div className="flex items-center justify-between sm:justify-end gap-3 sm:gap-4">
              <span className="text-gray-400 text-xs sm:text-sm whitespace-nowrap">
                Page {currentPage} of {totalPages}
              </span>
              <div className="flex gap-1">
                {/* First Page */}
                <button
                  onClick={() => setCurrentPage(1)}
                  disabled={currentPage === 1}
                  className="p-1.5 sm:p-2 bg-[#161b22] border border-[#30363d] rounded-lg hover:bg-[#1c2128] disabled:opacity-50 disabled:cursor-not-allowed transition"
                  aria-label="First page"
                >
                  <svg
                    className="w-3 h-3 sm:w-4 sm:h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
                    />
                  </svg>
                </button>
                {/* Previous Page */}
                <button
                  onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="p-1.5 sm:p-2 bg-[#161b22] border border-[#30363d] rounded-lg hover:bg-[#1c2128] disabled:opacity-50 disabled:cursor-not-allowed transition"
                  aria-label="Previous page"
                >
                  <svg
                    className="w-3 h-3 sm:w-4 sm:h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 19l-7-7 7-7"
                    />
                  </svg>
                </button>
                {/* Next Page */}
                <button
                  onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="p-1.5 sm:p-2 bg-[#161b22] border border-[#30363d] rounded-lg hover:bg-[#1c2128] disabled:opacity-50 disabled:cursor-not-allowed transition"
                  aria-label="Next page"
                >
                  <svg
                    className="w-3 h-3 sm:w-4 sm:h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </button>
                {/* Last Page */}
                <button
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={currentPage === totalPages}
                  className="p-1.5 sm:p-2 bg-[#161b22] border border-[#30363d] rounded-lg hover:bg-[#1c2128] disabled:opacity-50 disabled:cursor-not-allowed transition"
                  aria-label="Last page"
                >
                  <svg
                    className="w-3 h-3 sm:w-4 sm:h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 5l7 7-7 7M5 5l7 7-7 7"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}