import React, { useState, useRef } from 'react';
import { Upload as UploadIcon, FileVideo, CheckCircle, AlertCircle } from 'lucide-react';
import Button from './Button';
import { uploadVideo } from '../utils/api';

const UploadBox = () => {
    const [dragActive, setDragActive] = useState(false);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState(null);
    const [message, setMessage] = useState('');
    const inputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file) => {
        if (file.type.startsWith('video/')) {
            setFile(file);
            setUploadStatus(null);
            setMessage('');
        } else {
            setMessage('Please upload a valid video file.');
            setUploadStatus('error');
        }
    };

    const onButtonClick = () => {
        inputRef.current.click();
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        try {
            const result = await uploadVideo(file);
            setUploadStatus('success');
            setMessage(`Upload successful! Session ID: ${result.session_id}`);
        } catch (error) {
            setUploadStatus('error');
            setMessage('Upload failed. Please try again.');
            console.error(error);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-xl mx-auto mt-8">
            <div
                className={`relative border-2 border-dashed rounded-lg p-12 text-center ${dragActive ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'
                    }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    ref={inputRef}
                    type="file"
                    className="hidden"
                    accept="video/*"
                    onChange={handleChange}
                />

                {!file ? (
                    <div className="space-y-4">
                        <div className="flex justify-center">
                            <UploadIcon className="h-12 w-12 text-gray-400" />
                        </div>
                        <div>
                            <p className="text-lg font-medium text-gray-900">
                                Upload your teaching video
                            </p>
                            <p className="text-sm text-gray-500 mt-1">
                                Drag and drop or click to select
                            </p>
                        </div>
                        <Button onClick={onButtonClick} variant="outline">
                            Select Video
                        </Button>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="flex items-center justify-center space-x-2 text-indigo-600">
                            <FileVideo className="h-8 w-8" />
                            <span className="font-medium">{file.name}</span>
                        </div>
                        <div className="flex justify-center space-x-4">
                            <Button onClick={() => setFile(null)} variant="outline" disabled={uploading}>
                                Change
                            </Button>
                            <Button onClick={handleUpload} disabled={uploading}>
                                {uploading ? 'Uploading...' : 'Start Processing'}
                            </Button>
                        </div>
                    </div>
                )}
            </div>

            {message && (
                <div className={`mt-4 p-4 rounded-md flex items-center ${uploadStatus === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                    }`}>
                    {uploadStatus === 'success' ? (
                        <CheckCircle className="h-5 w-5 mr-2" />
                    ) : (
                        <AlertCircle className="h-5 w-5 mr-2" />
                    )}
                    {message}
                </div>
            )}
        </div>
    );
};

export default UploadBox;
