import React, { useState, ChangeEvent } from "react";
import { Upload, X } from "lucide-react";

interface ProductDescription {
  generated_description: string;
  highlights: string[];
  suggested_price_range?: string;
  original_description?: string;
}

type ToneOption = "professional" | "casual" | "luxury" | "technical";

interface FilePreview {
  file: File;
  preview: string;
}

const ProductDescriptionGenerator: React.FC = () => {
  const [files, setFiles] = useState<FilePreview[]>([]);
  const [descriptions, setDescriptions] = useState<ProductDescription[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [tone, setTone] = useState<ToneOption>("professional");

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;

    const selectedFiles = Array.from(e.target.files);
    const filePreviews: FilePreview[] = selectedFiles.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
    }));
    setFiles((prev) => [...prev, ...filePreviews]);
  };

  const removeFile = (indexToRemove: number) => {
    setFiles((prevFiles) => {
      // Revoke the URL for the removed file
      URL.revokeObjectURL(prevFiles[indexToRemove].preview);
      return prevFiles.filter((_, index) => index !== indexToRemove);
    });
  };

  const handleSubmit = async (): Promise<void> => {
    setLoading(true);
    const formData = new FormData();
    files.forEach(({ file }) => {
      formData.append("images", file);
    });
    formData.append("tone", tone);

    try {
      const response = await fetch("http://localhost:8000/generate-multiple", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to generate descriptions");
      }

      const data: ProductDescription[] = await response.json();
      setDescriptions(data);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  // Cleanup function for URL.createObjectURL
  React.useEffect(() => {
    return () => {
      files.forEach((file) => URL.revokeObjectURL(file.preview));
    };
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Product Description Generator</h1>

      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">Writing Tone</label>
        <select
          value={tone}
          onChange={(e) => setTone(e.target.value as ToneOption)}
          className="w-full p-2 border rounded"
        >
          <option value="professional">Professional</option>
          <option value="casual">Casual</option>
          <option value="luxury">Luxury</option>
          <option value="technical">Technical</option>
        </select>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">
          Upload Product Images
        </label>
        <div className="border-2 border-dashed rounded-lg p-6 text-center">
          <input
            type="file"
            multiple
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
            accept="image/*"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer flex flex-col items-center"
          >
            <Upload className="w-12 h-12 text-gray-400 mb-2" />
            <span className="text-sm text-gray-600">
              Drop files here or click to upload
            </span>
          </label>
        </div>
      </div>

      {files.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-medium mb-2">Selected Files:</h2>
          <div className="grid grid-cols-2 gap-4">
            {files.map((file, index) => (
              <div key={index} className="border rounded p-2 relative">
                <button
                  onClick={() => removeFile(index)}
                  className="absolute top-1 right-1 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                  title="Remove image"
                >
                  <X size={16} />
                </button>
                <img
                  src={file.preview}
                  alt={`Preview ${index + 1}`}
                  className="w-full h-48 object-cover rounded"
                />
                <p className="text-sm mt-2 truncate">{file.file.name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={loading || files.length === 0}
        className="w-full bg-blue-600 text-white p-3 rounded font-medium disabled:bg-gray-400"
      >
        {loading ? "Generating..." : "Generate Descriptions"}
      </button>

      {descriptions.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Generated Descriptions</h2>
          <div className="space-y-6">
            {descriptions.map((desc, index) => (
              <div key={index} className="border rounded-lg p-4">
                <h3 className="font-medium mb-2">Description {index + 1}</h3>
                <p className="text-gray-700 mb-4">
                  {desc.generated_description}
                </p>
                <div className="space-y-2">
                  <h4 className="font-medium">Key Highlights:</h4>
                  <ul className="list-disc pl-5">
                    {desc.highlights.map((highlight, i) => (
                      <li key={i} className="text-gray-600">
                        {highlight}
                      </li>
                    ))}
                  </ul>
                </div>
                {desc.suggested_price_range && (
                  <p className="mt-4 text-sm text-gray-500">
                    Suggested Price Range: {desc.suggested_price_range}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDescriptionGenerator;
