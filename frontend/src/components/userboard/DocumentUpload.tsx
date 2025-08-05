import React, { useState, useRef } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Alert, AlertDescription } from '../ui/alert';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { UploadProgress } from './UploadProgress';

interface DocumentUploadProps {
    onUploadSuccess?: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadSuccess }) => {
    const [isUploading, setIsUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            // Validate file type
            if (!file.type.includes('pdf')) {
                setError('Please select a PDF file');
                return;
            }

            // Validate file size (max 10MB)
            if (file.size > 10 * 1024 * 1024) {
                setError('File size must be less than 10MB');
                return;
            }

            setUploadedFile(file);
            setError(null);
        }
    };

    const uploadDocument = async () => {
        if (!uploadedFile) return;

        setIsUploading(true);
        setProgress(0);
        setError(null);

        try {
            // Simulate progress
            const progressInterval = setInterval(() => {
                setProgress(prev => {
                    if (prev >= 90) {
                        clearInterval(progressInterval);
                        return 90;
                    }
                    return prev + 10;
                });
            }, 200);

            // Get auth token
            const token = localStorage.getItem('accessToken');
            if (!token) {
                throw new Error('Authentication required');
            }

            // Create form data
            const formData = new FormData();
            formData.append('file', uploadedFile);

            // Upload document
            const response = await fetch('http://127.0.0.1:8000/agent/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData,
            });

            clearInterval(progressInterval);
            setProgress(100);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Upload failed: ${response.status}`);
            }

            const result = await response.json();

            // Success
            setTimeout(() => {
                setIsUploading(false);
                setUploadedFile(null);
                if (fileInputRef.current) {
                    fileInputRef.current.value = '';
                }
                onUploadSuccess?.();
            }, 1000);

        } catch (err) {
            clearInterval(progressInterval);
            setIsUploading(false);
            setError(err instanceof Error ? err.message : 'Upload failed');
        }
    };

    const handleRetry = () => {
        setError(null);
        if (uploadedFile) {
            uploadDocument();
        }
    };

    const handleClose = () => {
        setError(null);
        setIsUploading(false);
        setProgress(0);
        setUploadedFile(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="mt-4">
                    <label htmlFor="file-upload" className="cursor-pointer">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Click to upload a PDF document
                        </span>
                        <Input
                            ref={fileInputRef}
                            id="file-upload"
                            type="file"
                            accept=".pdf"
                            onChange={handleFileSelect}
                            className="hidden"
                        />
                    </label>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                    PDF files only, max 10MB
                </p>
            </div>

            {uploadedFile && (
                <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <FileText className="h-5 w-5 text-blue-500" />
                    <div className="flex-1">
                        <p className="text-sm font-medium">{uploadedFile.name}</p>
                        <p className="text-xs text-gray-500">
                            {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                    </div>
                    <Button
                        onClick={uploadDocument}
                        disabled={isUploading}
                        className="bg-blue-500 hover:bg-blue-600"
                    >
                        {isUploading ? 'Uploading...' : 'Upload'}
                    </Button>
                </div>
            )}

            {error && (
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            <UploadProgress
                isUploading={isUploading}
                progress={progress}
                error={error}
                onRetry={handleRetry}
                onClose={handleClose}
            />
        </div>
    );
}; 