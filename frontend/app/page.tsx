"use client";
import { useState } from "react";

interface TagData {
  title: string;
  artist: string;
  album: string;
  thumbnail?: string;
}

interface ExtractResponse {
  session_id: string;
  tags: TagData;
}

export default function Home() {
  const [url, setUrl] = useState("");
  const [downloadLink, setDownloadLink] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [showTagEditor, setShowTagEditor] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [tags, setTags] = useState<TagData>({
    title: "",
    artist: "",
    album: "",
    thumbnail: ""
  });
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [useUploadedImage, setUseUploadedImage] = useState(false);
  const [extractProgress, setExtractProgress] = useState(0);

  const simulateProgress = () => {
    setExtractProgress(0);
    const interval = setInterval(() => {
      setExtractProgress(prev => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90; // Stop at 90% until actual completion
        }
        return prev + Math.random() * 15;
      });
    }, 300);
    return interval;
  };

  const handleExtractInfo = async () => {
    if (!url) return;
    setExtracting(true);
    setLoading(false);
    setDownloadLink(null);
    setShowTagEditor(false);
    setUploadedImage(null);
    setImagePreview(null);
    setUseUploadedImage(false);

    const progressInterval = simulateProgress();

    try {
      const res = await fetch(
          `http://127.0.0.1:8000/extract-info?youtube_url=${encodeURIComponent(url)}`
      );
      if (!res.ok) throw new Error("Failed to extract info");

      const data: ExtractResponse = await res.json();

      // Complete the progress
      clearInterval(progressInterval);
      setExtractProgress(100);

      // Small delay to show 100% completion
      setTimeout(() => {
        setSessionId(data.session_id);
        setTags(data.tags);
        setShowTagEditor(true);
        setExtracting(false);
        setExtractProgress(0);
      }, 500);

    } catch (err) {
      clearInterval(progressInterval);
      setExtracting(false);
      setExtractProgress(0);
      alert((err as Error).message);
    }
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedImage(file);
      setUseUploadedImage(true);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDownloadWithTags = async () => {
    if (!sessionId) return;
    setLoading(true);

    try {
      // Upload image if user selected one
      if (useUploadedImage && uploadedImage) {
        const formData = new FormData();
        formData.append('file', uploadedImage);

        const uploadRes = await fetch(`http://127.0.0.1:8000/upload-image/${sessionId}`, {
          method: 'POST',
          body: formData,
        });

        if (!uploadRes.ok) throw new Error("Failed to upload image");
      }

      // Download with tags
      const res = await fetch(`http://127.0.0.1:8000/download/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...tags,
          thumbnail: useUploadedImage ? "" : tags.thumbnail // Clear thumbnail URL if using uploaded image
        }),
      });

      if (!res.ok) throw new Error("Download failed");

      const blob = await res.blob();
      const link = URL.createObjectURL(blob);
      setDownloadLink(link);
      setShowTagEditor(false);
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleTagChange = (field: keyof TagData, value: string) => {
    setTags(prev => ({ ...prev, [field]: value }));
  };

  const getCurrentThumbnail = () => {
    if (useUploadedImage && imagePreview) {
      return imagePreview;
    }
    return tags.thumbnail;
  };

  return (
      <main className="flex flex-col items-center p-10 max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">YouTube → Tagged MP3</h1>

        {!showTagEditor && !extracting && (
            <div className="w-full">
              <div className="flex mb-4">
                <input
                    type="text"
                    placeholder="Paste YouTube link"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="border p-2 flex-1 rounded-l"
                />
                <button
                    onClick={handleExtractInfo}
                    disabled={extracting || !url}
                    className="px-4 py-2 bg-blue-500 text-white rounded-r disabled:bg-gray-400"
                >
                  Extract Info
                </button>
              </div>
            </div>
        )}

        {extracting && (
            <div className="w-full max-w-md">
              <div className="text-center mb-4">
                <h2 className="text-lg font-semibold mb-2">Extracting video information...</h2>
                <p className="text-gray-600 text-sm">This may take a few moments</p>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                <div
                    className="bg-green-500 h-3 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${extractProgress}%` }}
                ></div>
              </div>

              {/* Progress Text */}
              <div className="text-center text-sm text-gray-600">
                {extractProgress < 30 && "Connecting to YouTube..."}
                {extractProgress >= 30 && extractProgress < 60 && "Downloading audio..."}
                {extractProgress >= 60 && extractProgress < 90 && "Processing metadata..."}
                {extractProgress >= 90 && extractProgress < 100 && "Almost done..."}
                {extractProgress === 100 && "Complete!"}
              </div>

              {/* Animated dots */}
              <div className="flex justify-center mt-4">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
        )}

        {showTagEditor && (
            <div className="w-full bg-gray-900 p-6 rounded-lg">
              <h2 className="text-xl font-semibold mb-4">Edit Tags</h2>

              {getCurrentThumbnail() && (
                  <div className="mb-4 flex justify-center">
                    <img
                        src={getCurrentThumbnail()}
                        alt="Thumbnail"
                        className="w-32 h-32 object-cover rounded"
                    />
                  </div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Title</label>
                  <input
                      type="text"
                      value={tags.title}
                      onChange={(e) => handleTagChange('title', e.target.value)}
                      className="w-full border p-2 rounded"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Artist</label>
                  <input
                      type="text"
                      value={tags.artist}
                      onChange={(e) => handleTagChange('artist', e.target.value)}
                      className="w-full border p-2 rounded"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Album</label>
                  <input
                      type="text"
                      value={tags.album}
                      onChange={(e) => handleTagChange('album', e.target.value)}
                      className="w-full border p-2 rounded"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Album Art</label>

                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <input
                          type="radio"
                          id="use-url"
                          name="image-source"
                          checked={!useUploadedImage}
                          onChange={() => setUseUploadedImage(false)}
                          className="w-4 h-4"
                      />
                      <label htmlFor="use-url" className="text-sm">Use thumbnail URL</label>
                    </div>

                    {!useUploadedImage && (
                        <input
                            type="text"
                            value={tags.thumbnail || ''}
                            onChange={(e) => handleTagChange('thumbnail', e.target.value)}
                            placeholder="Thumbnail URL"
                            className="w-full border p-2 rounded"
                        />
                    )}

                    <div className="flex items-center space-x-2">
                      <input
                          type="radio"
                          id="use-upload"
                          name="image-source"
                          checked={useUploadedImage}
                          onChange={() => setUseUploadedImage(true)}
                          className="w-4 h-4"
                      />
                      <label htmlFor="use-upload" className="text-sm">Upload custom image</label>
                    </div>

                    {useUploadedImage && (
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            className="w-full border p-2 rounded"
                        />
                    )}
                  </div>
                </div>
              </div>

              <div className="flex gap-2 mt-6">
                <button
                    onClick={handleDownloadWithTags}
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-green-500 text-white rounded disabled:bg-gray-400"
                >
                  {loading ? "Downloading..." : "Download MP3"}
                </button>
                <button
                    onClick={() => setShowTagEditor(false)}
                    className="px-4 py-2 bg-gray-500 text-white rounded"
                >
                  Back
                </button>
              </div>
            </div>
        )}

        {downloadLink && (
            <div className="mt-6 text-center">
              <a
                  href={downloadLink}
                  download={`${tags.title || 'song'}.mp3`}
                  className="text-green-600 underline text-lg"
              >
                Download your MP3
              </a>
            </div>
        )}
      </main>
  );
}