"use client";

import { BACKEND_URL } from "@/config";
import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

interface Repo {
  id: number;
  full_name: string;
  description?: string | null;
  stargazers_count: number;
  forks_count: number;
  watchers_count: number;
  html_url: string;
}

export default function Page() {
  const params = useParams();
  const searchParams = useSearchParams();

  const owner = params.owner as string;
  const repo = params.repo as string;
  const installationId = searchParams.get("installation_id");

  // Debug logging
  console.log("Params:", params);
  console.log("Owner:", owner);
  console.log("Repo:", repo);
  console.log("Installation ID:", installationId);

  const [repoData, setRepoData] = useState<Repo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const handleApply = async () => {
    if (!repoData || !installationId) {
      console.error("Missing repo data or installation ID");
      return;
    }

    try {
      const res = await fetch(`${BACKEND_URL}/github/select`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          github_repo_id: repoData.id,
          installation_id: Number(installationId),
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Error: ${res.status} - ${errorText}`);
      }

      const data = await res.json();
      console.log("Successfully applied:", data);
    } catch (err) {
      console.error("Failed to apply:",  err);
    }
  };

  useEffect(() => {
    async function fetchRepo() {
      if (!owner || !repo || !installationId) {
        setError(
          `Missing owner (${owner}), repo (${repo}), or installation ID (${installationId})`
        );
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const url = `http://localhost:8000/repo/${repo}?installation_id=${Number(
          installationId
        )}&owner=${owner}`;
        console.log("Fetching:", url);

        const res = await fetch(url, {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });

        if (!res.ok) {
          const errText = await res.text();
          throw new Error(`Error fetching repo: ${res.status} - ${errText}`);
        }

        const data: Repo = await res.json();
        setRepoData(data);
      } catch (err) {
        console.error("Failed to fetch repo:", err);
        setError("Unknown error");
      } finally {
        setLoading(false);
      }
    }

    fetchRepo();
  }, [owner, repo, installationId]);

  // Show what we're rendering
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 p-6 text-white">
        <p>
          Loading repo details for {owner}/{repo}...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 p-6 text-red-400">
        <p>Error: {error}</p>
      </div>
    );
  }

  if (!repoData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 p-6 text-white">
        <p>No repo found.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 p-6 text-white">
      <h1 className="text-3xl font-bold mb-4">{repoData.full_name}</h1>

      {/* Repo ID */}
      <p className="text-sm text-purple-400 mb-4">
        Repository ID: {repoData.id}
      </p>

      <p className="text-slate-300 mb-4">
        {repoData.description || "No description"}
      </p>

      <div className="space-y-2 mb-6">
        <p className="text-slate-400">⭐ {repoData.stargazers_count} stars</p>
        <p className="text-slate-400">🍴 {repoData.forks_count} forks</p>
        <p className="text-slate-400">👀 {repoData.watchers_count} watchers</p>
      </div>

      <div className="flex justify-start items-center gap-4">
        <a
          href={repoData.html_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 inline-block px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded transition"
        >
          View on GitHub
        </a>

        <button onClick={handleApply} className="p-4 bg-gray-600 rounded-lg">
          apply
        </button>
      </div>
    </div>
  );
}
