// components/userboard/DocumentAgentTab.tsx
import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
    Upload,
    Search,
    FileText,
    BarChart3,
    CheckCircle,
    AlertCircle,
    Loader2,
    File,
    Trash2,
    Download
} from 'lucide-react';
import { DocumentAgentService, type DocumentInfo, type DocumentAnalytics } from '../../lib/documentAgentService';

interface DocumentAgentTabProps {
    onSendMessage: (message: string) => Promise<void>;
    onSwitchToChat?: () => void;
    uploadedDocuments?: UploadedDocument[];
    setUploadedDocuments?: React.Dispatch<React.SetStateAction<UploadedDocument[]>>;
}

interface UploadedDocument {
    id: string;
    name: string;
    size: number;
    type: string;
    uploadDate: string;
    status: 'uploading' | 'processing' | 'completed' | 'failed';
    progress?: number;
    pages?: number;
    error?: string;
}

export function DocumentAgentTab({ onSendMessage, onSwitchToChat, uploadedDocuments = [], setUploadedDocuments }: DocumentAgentTabProps) {
    const [documentInfo, setDocumentInfo] = useState<DocumentInfo | null>(null);
    const [analytics, setAnalytics] = useState<DocumentAnalytics | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<string>('');
    const [isSearching, setIsSearching] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadDocumentInfo();
        loadAnalytics();
    }, []);

    const loadDocumentInfo = async () => {
        try {
            const info = await DocumentAgentService.getDocumentInfo();
            setDocumentInfo(info);
        } catch (err) {
            console.error('Failed to load document info:', err);
            setError('Failed to load document information');
        }
    };

    const loadAnalytics = async () => {
        try {
            const analyticsData = await DocumentAgentService.getDocumentAnalytics();
            setAnalytics(analyticsData);
        } catch (err) {
            console.error('Failed to load analytics:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        setIsUploading(true);
        setError(null);

        for (const file of Array.from(files)) {
            const document: UploadedDocument = {
                id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
                name: file.name,
                size: file.size,
                type: file.type,
                uploadDate: new Date().toISOString(),
                status: 'uploading',
                progress: 0
            };

            setUploadedDocuments?.(prev => [...prev, document]);

            try {
                // Simulate upload progress
                const progressInterval = setInterval(() => {
                    setUploadedDocuments?.(prev => prev.map(doc => {
                        if (doc.id === document.id && doc.progress! < 90) {
                            return { ...doc, progress: doc.progress! + 10 };
                        }
                        return doc;
                    }));
                }, 100);

                // Upload document
                const result = await DocumentAgentService.uploadDocument(file);

                clearInterval(progressInterval);

                if (result.success) {
                    setUploadedDocuments?.(prev => prev.map(doc => {
                        if (doc.id === document.id) {
                            return {
                                ...doc,
                                status: 'completed',
                                progress: 100,
                                pages: result.pages_processed
                            };
                        }
                        return doc;
                    }));

                    // Reload document info and analytics
                    await loadDocumentInfo();
                    await loadAnalytics();
                } else {
                    setUploadedDocuments?.(prev => prev.map(doc => {
                        if (doc.id === document.id) {
                            return {
                                ...doc,
                                status: 'failed',
                                error: result.error || 'Upload failed'
                            };
                        }
                        return doc;
                    }));
                }
            } catch (err) {
                console.error('Upload failed:', err);
                setUploadedDocuments?.(prev => prev.map(doc => {
                    if (doc.id === document.id) {
                        return {
                            ...doc,
                            status: 'failed',
                            error: err instanceof Error ? err.message : 'Upload failed'
                        };
                    }
                    return doc;
                }));
            }
        }

        setIsUploading(false);
        // Clear the input
        event.target.value = '';
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) return;

        setIsSearching(true);
        setError(null);

        try {
            const result = await DocumentAgentService.searchDocuments(searchQuery);

            if (result.success) {
                setSearchResults(result.response || 'No results found');
            } else {
                setError(result.error || 'Search failed');
            }
        } catch (err) {
            console.error('Search failed:', err);
            setError(err instanceof Error ? err.message : 'Search failed');
        } finally {
            setIsSearching(false);
        }
    };

    const handleDocumentQuery = async (query: string) => {
        try {
            await onSendMessage(`[Document Query] ${query}`);
            // Switch to chat tab to show the response
            if (onSwitchToChat) {
                onSwitchToChat();
            }
        } catch (err) {
            console.error('Failed to send document query:', err);
        }
    };

    const removeDocument = (documentId: string) => {
        setUploadedDocuments?.(prev => prev.filter(doc => doc.id !== documentId));
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="h-4 w-4 text-green-500" />;
            case 'failed':
                return <AlertCircle className="h-4 w-4 text-red-500" />;
            case 'uploading':
            case 'processing':
                return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
            default:
                return <File className="h-4 w-4 text-gray-500" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
            case 'failed':
                return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
            case 'uploading':
            case 'processing':
                return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
            default:
                return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-center">
                    <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
                    <p className="text-muted-foreground">Loading document information...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col min-h-full overflow-y-auto p-4 space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Document Agent</h2>
                    <p className="text-muted-foreground">Upload, search, and analyze your documents</p>
                </div>
                <div className="flex items-center space-x-2">
                    <Badge variant="outline">
                        {documentInfo?.documents_indexed || 0} Documents
                    </Badge>
                    <Badge variant="outline">
                        {documentInfo?.qdrant_documents || 0} in QDRANT
                    </Badge>
                    <Badge variant="outline">
                        {analytics?.total_pages || 0} Pages
                    </Badge>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            {/* Upload Section */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <Upload className="h-5 w-5" />
                        <span>Upload Documents</span>
                    </CardTitle>
                    <CardDescription>
                        Upload PDF documents to be processed and indexed for search
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center space-x-4">
                        <Input
                            type="file"
                            accept=".pdf"
                            onChange={handleFileUpload}
                            disabled={isUploading}
                            className="flex-1"
                        />
                        {isUploading && (
                            <div className="flex items-center space-x-2">
                                <Loader2 className="h-4 w-4 animate-spin" />
                                <span className="text-sm text-muted-foreground">Uploading...</span>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Document List */}
            {uploadedDocuments.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Recent Uploads</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {uploadedDocuments.map((doc) => (
                                <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        {getStatusIcon(doc.status)}
                                        <div>
                                            <p className="font-medium">{doc.name}</p>
                                            <p className="text-sm text-muted-foreground">
                                                {doc.pages ? `${doc.pages} pages` : `${(doc.size / 1024 / 1024).toFixed(2)} MB`}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <Badge className={getStatusColor(doc.status)}>
                                            {doc.status}
                                        </Badge>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => removeDocument(doc.id)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                    {doc.status === 'uploading' && doc.progress && (
                                        <Progress value={doc.progress} className="w-20" />
                                    )}
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Search Section */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <Search className="h-5 w-5" />
                        <span>Search Documents</span>
                    </CardTitle>
                    <CardDescription>
                        Search through your uploaded documents
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div className="flex space-x-2">
                            <Input
                                placeholder="Enter your search query..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                                disabled={isSearching}
                            />
                            <Button onClick={handleSearch} disabled={isSearching || !searchQuery.trim()}>
                                {isSearching ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Search className="h-4 w-4" />
                                )}
                            </Button>
                        </div>
                        {searchResults && (
                            <div className="p-4 bg-muted rounded-lg">
                                <h4 className="font-medium mb-2">Search Results:</h4>
                                <p className="text-sm">{searchResults}</p>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <BarChart3 className="h-5 w-5" />
                        <span>Quick Actions</span>
                    </CardTitle>
                    <CardDescription>
                        Common document analysis tasks
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 gap-3">
                        <Button
                            variant="outline"
                            onClick={() => handleDocumentQuery("Summarize all uploaded documents")}
                            className="h-auto p-3 flex-col space-y-2"
                        >
                            <FileText className="h-5 w-5" />
                            <span className="text-sm">Summarize Documents</span>
                        </Button>
                        <Button
                            variant="outline"
                            onClick={() => handleDocumentQuery("What are the key topics in my documents?")}
                            className="h-auto p-3 flex-col space-y-2"
                        >
                            <BarChart3 className="h-5 w-5" />
                            <span className="text-sm">Key Topics</span>
                        </Button>
                        <Button
                            variant="outline"
                            onClick={() => handleDocumentQuery("Extract important dates and deadlines from my documents")}
                            className="h-auto p-3 flex-col space-y-2"
                        >
                            <FileText className="h-5 w-5" />
                            <span className="text-sm">Extract Dates</span>
                        </Button>
                        <Button
                            variant="outline"
                            onClick={() => handleDocumentQuery("Compare and contrast the main points across all documents")}
                            className="h-auto p-3 flex-col space-y-2"
                        >
                            <BarChart3 className="h-5 w-5" />
                            <span className="text-sm">Compare Documents</span>
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Analytics */}
            {analytics && (
                <Card>
                    <CardHeader>
                        <CardTitle>Document Analytics</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <div className="flex items-center justify-center py-8">
                                <Loader2 className="h-6 w-6 animate-spin" />
                                <span className="ml-2">Loading analytics...</span>
                            </div>
                        ) : (
                            <div className="grid grid-cols-4 gap-4">
                                <div className="text-center">
                                    <p className="text-2xl font-bold">{analytics.total_documents || 0}</p>
                                    <p className="text-sm text-muted-foreground">Total Documents</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-2xl font-bold">{analytics.total_pages || 0}</p>
                                    <p className="text-sm text-muted-foreground">Total Pages</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-2xl font-bold">{analytics.embeddings_generated || 0}</p>
                                    <p className="text-sm text-muted-foreground">Embeddings</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-2xl font-bold">{analytics.document_types ? Object.keys(analytics.document_types).length : 0}</p>
                                    <p className="text-sm text-muted-foreground">Document Types</p>
                                </div>
                            </div>
                        )}
                        {analytics.recent_uploads && analytics.recent_uploads.length > 0 && (
                            <div className="mt-4">
                                <h4 className="font-medium mb-2">Recent Uploads:</h4>
                                <div className="space-y-2">
                                    {analytics.recent_uploads.slice(0, 3).map((upload, index) => (
                                        <div key={index} className="flex justify-between text-sm">
                                            <span>{upload.name}</span>
                                            <span className="text-muted-foreground">{upload.pages} pages</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}
        </div>
    );
} 