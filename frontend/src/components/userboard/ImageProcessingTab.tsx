import React, { useState, useRef, useCallback } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import {
    Upload,
    Image as ImageIcon,
    Search,
    FileText,
    BarChart3,
    CheckCircle,
    AlertCircle,
    Loader2,
    File,
    Trash2,
    Download,
    Eye,
    Settings,
    Palette,
    Crop,
    RotateCw,
    ZoomIn,
    Filter
} from 'lucide-react';

interface ProcessedImage {
    id: string;
    name: string;
    originalUrl: string;
    processedUrl?: string;
    size: number;
    type: string;
    uploadDate: string;
    status: 'uploading' | 'processing' | 'completed' | 'failed';
    progress?: number;
    error?: string;
    metadata?: {
        width: number;
        height: number;
        format: string;
        size: string;
    };
    analysis?: {
        objects: string[];
        text: string[];
        colors: string[];
        confidence: number;
    };
}

interface ImageProcessingTabProps {
    onSendMessage: (message: string) => Promise<void>;
}

export function ImageProcessingTab({ onSendMessage }: ImageProcessingTabProps) {
    const [images, setImages] = useState<ProcessedImage[]>([]);
    const [selectedImage, setSelectedImage] = useState<ProcessedImage | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<string>('');
    const [isSearching, setIsSearching] = useState(false);
    const [processingOptions, setProcessingOptions] = useState({
        extractText: true,
        detectObjects: true,
        analyzeColors: true,
        enhanceQuality: false,
        resize: false,
        targetWidth: 800,
        targetHeight: 600
    });

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        Array.from(files).forEach(file => {
            if (!file.type.startsWith('image/')) {
                alert('Please select image files only');
                return;
            }

            const image: ProcessedImage = {
                id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
                name: file.name,
                originalUrl: URL.createObjectURL(file),
                size: file.size,
                type: file.type,
                uploadDate: new Date().toISOString(),
                status: 'uploading',
                progress: 0
            };

            setImages(prev => [...prev, image]);
            processImage(image, file);
        });
    };

    const processImage = async (image: ProcessedImage, file: File) => {
        try {
            setIsUploading(true);

            // Simulate upload progress
            const progressInterval = setInterval(() => {
                setImages(prev => prev.map(img => {
                    if (img.id === image.id) {
                        const newProgress = Math.min((img.progress || 0) + 10, 90);
                        return { ...img, progress: newProgress };
                    }
                    return img;
                }));
            }, 200);

            // Get auth token
            const token = localStorage.getItem('access_token');
            if (!token) {
                throw new Error('Authentication required');
            }

            // Create form data
            const formData = new FormData();
            formData.append('file', file);
            formData.append('processing_options', JSON.stringify(processingOptions));

            // Upload and process image
            const response = await fetch('http://127.0.0.1:8000/agent/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData,
            });

            clearInterval(progressInterval);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Processing failed: ${response.status}`);
            }

            const result = await response.json();

            // Update image with processing results
            setImages(prev => prev.map(img => {
                if (img.id === image.id) {
                    return {
                        ...img,
                        status: 'completed',
                        progress: 100,
                        analysis: result.analysis || {
                            objects: [],
                            text: [],
                            colors: [],
                            confidence: 0.8
                        }
                    };
                }
                return img;
            }));

        } catch (error) {
            setImages(prev => prev.map(img => {
                if (img.id === image.id) {
                    return {
                        ...img,
                        status: 'failed',
                        error: error instanceof Error ? error.message : 'Processing failed'
                    };
                }
                return img;
            }));
        } finally {
            setIsUploading(false);
        }
    };

    const handleImageQuery = async (query: string) => {
        if (!selectedImage) {
            alert('Please select an image first');
            return;
        }

        try {
            setIsSearching(true);

            const message = `[Image Query] ${query} - Image: ${selectedImage.name}`;
            await onSendMessage(message);

            setSearchResults(`Query processed for image: ${selectedImage.name}`);
        } catch (error) {
            setSearchResults(`Error processing query: ${error}`);
        } finally {
            setIsSearching(false);
        }
    };

    const handleImageAnalysis = async () => {
        if (!selectedImage) {
            alert('Please select an image first');
            return;
        }

        try {
            setIsProcessing(true);

            const analysisQuery = `Analyze this image: ${selectedImage.name}. Extract text, detect objects, and analyze colors.`;
            await onSendMessage(analysisQuery);

        } catch (error) {
            console.error('Image analysis failed:', error);
        } finally {
            setIsProcessing(false);
        }
    };

    const removeImage = (imageId: string) => {
        setImages(prev => prev.filter(img => img.id !== imageId));
        if (selectedImage?.id === imageId) {
            setSelectedImage(null);
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'uploading':
                return <Loader2 className="h-4 w-4 animate-spin" />;
            case 'processing':
                return <Loader2 className="h-4 w-4 animate-spin" />;
            case 'completed':
                return <CheckCircle className="h-4 w-4 text-green-500" />;
            case 'failed':
                return <AlertCircle className="h-4 w-4 text-red-500" />;
            default:
                return <File className="h-4 w-4" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'bg-green-100 text-green-800';
            case 'failed':
                return 'bg-red-100 text-red-800';
            case 'processing':
                return 'bg-blue-100 text-blue-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Image Processing</h2>
                    <p className="text-muted-foreground">
                        Upload and process images with ColPali AI analysis
                    </p>
                </div>
                <Button onClick={() => fileInputRef.current?.click()}>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Images
                </Button>
            </div>

            <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
            />

            <Tabs defaultValue="upload" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="upload">Upload & Process</TabsTrigger>
                    <TabsTrigger value="analysis">Image Analysis</TabsTrigger>
                    <TabsTrigger value="settings">Processing Settings</TabsTrigger>
                </TabsList>

                <TabsContent value="upload" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Processing Options</CardTitle>
                            <CardDescription>
                                Configure how images should be processed
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        id="extractText"
                                        checked={processingOptions.extractText}
                                        onChange={(e) => setProcessingOptions(prev => ({
                                            ...prev,
                                            extractText: e.target.checked
                                        }))}
                                    />
                                    <label htmlFor="extractText">Extract Text (OCR)</label>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        id="detectObjects"
                                        checked={processingOptions.detectObjects}
                                        onChange={(e) => setProcessingOptions(prev => ({
                                            ...prev,
                                            detectObjects: e.target.checked
                                        }))}
                                    />
                                    <label htmlFor="detectObjects">Detect Objects</label>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        id="analyzeColors"
                                        checked={processingOptions.analyzeColors}
                                        onChange={(e) => setProcessingOptions(prev => ({
                                            ...prev,
                                            analyzeColors: e.target.checked
                                        }))}
                                    />
                                    <label htmlFor="analyzeColors">Analyze Colors</label>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <input
                                        type="checkbox"
                                        id="enhanceQuality"
                                        checked={processingOptions.enhanceQuality}
                                        onChange={(e) => setProcessingOptions(prev => ({
                                            ...prev,
                                            enhanceQuality: e.target.checked
                                        }))}
                                    />
                                    <label htmlFor="enhanceQuality">Enhance Quality</label>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {images.map((image) => (
                            <Card key={image.id} className="relative">
                                <CardContent className="p-4">
                                    <div className="aspect-square relative mb-4">
                                        <img
                                            src={image.originalUrl}
                                            alt={image.name}
                                            className="w-full h-full object-cover rounded-lg"
                                        />
                                        {image.progress !== undefined && image.progress < 100 && (
                                            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                                                <Progress value={image.progress} className="w-3/4" />
                                            </div>
                                        )}
                                    </div>

                                    <div className="space-y-2">
                                        <div className="flex items-center justify-between">
                                            <h3 className="font-medium truncate">{image.name}</h3>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => removeImage(image.id)}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>

                                        <div className="flex items-center space-x-2">
                                            {getStatusIcon(image.status)}
                                            <Badge className={getStatusColor(image.status)}>
                                                {image.status}
                                            </Badge>
                                        </div>

                                        {image.analysis && (
                                            <div className="text-sm text-muted-foreground">
                                                <div>Objects: {image.analysis.objects.length}</div>
                                                <div>Text: {image.analysis.text.length} items</div>
                                                <div>Confidence: {(image.analysis.confidence * 100).toFixed(1)}%</div>
                                            </div>
                                        )}

                                        {image.error && (
                                            <Alert>
                                                <AlertCircle className="h-4 w-4" />
                                                <AlertDescription>{image.error}</AlertDescription>
                                            </Alert>
                                        )}
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </TabsContent>

                <TabsContent value="analysis" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Image Analysis</CardTitle>
                            <CardDescription>
                                Analyze selected images with ColPali AI
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex space-x-2">
                                <Input
                                    placeholder="Ask about the selected image..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                                <Button
                                    onClick={() => handleImageQuery(searchQuery)}
                                    disabled={!selectedImage || isSearching}
                                >
                                    {isSearching ? (
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                        <Search className="h-4 w-4" />
                                    )}
                                </Button>
                                <Button
                                    onClick={handleImageAnalysis}
                                    disabled={!selectedImage || isProcessing}
                                    variant="outline"
                                >
                                    {isProcessing ? (
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                        <BarChart3 className="h-4 w-4" />
                                    )}
                                    Analyze
                                </Button>
                            </div>

                            {searchResults && (
                                <Alert>
                                    <FileText className="h-4 w-4" />
                                    <AlertDescription>{searchResults}</AlertDescription>
                                </Alert>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="settings" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Processing Settings</CardTitle>
                            <CardDescription>
                                Configure image processing parameters
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm font-medium">Target Width</label>
                                    <Input
                                        type="number"
                                        value={processingOptions.targetWidth}
                                        onChange={(e) => setProcessingOptions(prev => ({
                                            ...prev,
                                            targetWidth: parseInt(e.target.value)
                                        }))}
                                    />
                                </div>
                                <div>
                                    <label className="text-sm font-medium">Target Height</label>
                                    <Input
                                        type="number"
                                        value={processingOptions.targetHeight}
                                        onChange={(e) => setProcessingOptions(prev => ({
                                            ...prev,
                                            targetHeight: parseInt(e.target.value)
                                        }))}
                                    />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
} 