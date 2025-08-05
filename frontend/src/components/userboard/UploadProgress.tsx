import React, { useState } from 'react';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { Button } from '../ui/button';
import { Upload, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface UploadProgressProps {
    isUploading: boolean;
    progress: number;
    error: string | null;
    onRetry: () => void;
    onClose: () => void;
}

export const UploadProgress: React.FC<UploadProgressProps> = ({
    isUploading,
    progress,
    error,
    onRetry,
    onClose
}) => {
    const [isVisible, setIsVisible] = useState(true);

    const handleClose = () => {
        setIsVisible(false);
        onClose();
    };

    if (!isVisible) return null;

    return (
        <div className="fixed bottom-4 right-4 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4 z-50">
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                    {isUploading ? (
                        <Upload className="h-5 w-5 text-blue-500 animate-pulse" />
                    ) : error ? (
                        <XCircle className="h-5 w-5 text-red-500" />
                    ) : (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                    )}
                    <span className="font-medium text-sm">
                        {isUploading ? 'Uploading Document...' : error ? 'Upload Failed' : 'Upload Complete'}
                    </span>
                </div>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleClose}
                    className="h-6 w-6 p-0"
                >
                    ×
                </Button>
            </div>

            {isUploading && (
                <div className="space-y-2">
                    <Progress value={progress} className="h-2" />
                    <div className="flex justify-between text-xs text-gray-500">
                        <span>Processing...</span>
                        <span>{progress}%</span>
                    </div>
                </div>
            )}

            {error && (
                <Alert variant="destructive" className="mt-3">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-sm">
                        {error}
                    </AlertDescription>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={onRetry}
                        className="mt-2"
                    >
                        Retry Upload
                    </Button>
                </Alert>
            )}

            {!isUploading && !error && (
                <div className="flex items-center space-x-2 text-sm text-green-600 dark:text-green-400">
                    <CheckCircle className="h-4 w-4" />
                    <span>Document uploaded and processed successfully!</span>
                </div>
            )}
        </div>
    );
}; 