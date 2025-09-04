"use client";
import { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [downloadLink, setDownloadLink] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleDownload = async () => {
    if (!url) return;
    setLoading(true);
    setDownloadLink(null);

    try {
      const res = await fetch(
          `http://127.0.0.1:8000/download?youtube_url=${encodeURIComponent(url)}`
      );
      if (!res.ok) throw new Error("Download failed");
      const blob = await res.blob();
      const link = URL.createObjectURL(blob);
      setDownloadLink(link);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
      <main className="flex flex-col items-center p-10">
        <h1 className="text-3xl font-bold mb-6">YouTube → MP3 (Spotify-ready)</h1>
        <div className="flex">
          <input
              type="text"
              placeholder="Paste YouTube link"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="border p-2 w-80"
          />
          <button
              onClick={handleDownload}
              className="ml-2 px-4 py-2 bg-blue-500 text-white rounded"
          >
            {loading ? "Processing..." : "Convert"}
          </button>
        </div>
        {downloadLink && (
            <a
                href={downloadLink}
                download="song.mp3"
                className="mt-6 text-green-600 underline"
            >
              Download your MP3
            </a>
        )}
      </main>
  );
}
