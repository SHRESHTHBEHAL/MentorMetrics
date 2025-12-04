import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, FileVideo, X } from 'lucide-react';
import Button from './Button';
import LoadingButton from './ui/LoadingButton';
import { uploadVideo } from '../utils/uploadAdapter';
import { processSession } from '../utils/api';
import { useToast } from './ui/ToastProvider';

const VideoPicker = ({ onFileSelect, dragActive, onDragEnter, onDragLeave, onDragOver, onDrop }) => {
    const inputRef = useRef(null);

    const onButtonClick = () => {
        inputRef.current.click();
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            onFileSelect(e.target.files[0]);
        }
    };

    return (
        <div
            className={`relative border-4 border-dashed rounded-none p-6 sm:p-12 text-center transition-all duration-200 ease-in-out ${dragActive ? 'border-black bg-gray-100' : 'border-black hover:bg-gray-50'
                }`}
            onDragEnter={onDragEnter}
            onDragLeave={onDragLeave}
            onDragOver={onDragOver}
            onDrop={onDrop}
        >
            <input
                ref={inputRef}
                type="file"
                className="hidden"
                accept=".mp4,.mov,.webm"
                onChange={handleChange}
            />
            <div className="space-y-6">
                <div className="flex justify-center">
                    <div className={`p-4 border-2 border-black ${dragActive ? 'bg-black text-white' : 'bg-white text-black'}`}>
                        <UploadIcon className="h-12 w-12 sm:h-16 sm:w-16" />
                    </div>
                </div>
                <div>
                    <p className="text-xl sm:text-2xl font-black uppercase text-black">
                        Upload your teaching video
                    </p>
                    <p className="text-sm sm:text-base font-bold text-gray-600 mt-2 uppercase">
                        Drag and drop or click to select
                    </p>
                    <p className="text-xs font-bold text-gray-400 mt-2 uppercase">
                        MP4, MOV, WEBM (MAX 50MB)
                    </p>
                </div>
                <button
                    onClick={onButtonClick}
                    className="w-full sm:w-auto px-8 py-3 bg-white text-black border-4 border-black font-black uppercase hover:bg-black hover:text-white transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                >
                    Select Video
                </button>
            </div>
        </div>
    );
};

const UploadBox = () => {
    const navigate = useNavigate();
    const { showError, showSuccess } = useToast();
    const [dragActive, setDragActive] = useState(false);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);

    const MAX_FILE_SIZE = 50 * 1024 * 1024;

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleFileSelection = (selectedFile) => {
        if (selectedFile.size > MAX_FILE_SIZE) {
            showError('File size must be under 50MB');
            return;
        }
        setFile(selectedFile);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const selectedFile = e.dataTransfer.files[0];
            if (selectedFile.size > MAX_FILE_SIZE) {
                showError('File size must be under 50MB');
                return;
            }
            setFile(selectedFile);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        setProgress(0);

        try {
            const uploadResult = await uploadVideo(file, (percent) => {
                setProgress(percent);
            });

            if (uploadResult.user_id) {
                localStorage.setItem('user_id', uploadResult.user_id);
            }

            showSuccess('Upload successful! Starting processing...');

            try {
                await processSession(uploadResult.session_id);
            } catch (processError) {
                console.warn('Failed to auto-start processing:', processError);
            }

            navigate(`/status?session_id=${uploadResult.session_id}`);
        } catch (err) {
            console.error(err);
            showError(err.message || 'Upload failed.');
            setUploading(false);
            setProgress(0);
        }
    };

    const clearFile = () => {
        setFile(null);
        setProgress(0);
    };

    return (
        <div className="max-w-xl mx-auto mt-8">
            {!file ? (
                <VideoPicker
                    onFileSelect={handleFileSelection}
                    dragActive={dragActive}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                />
            ) : (
                <div className="bg-white p-6 sm:p-8 border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] text-center space-y-8">
                    <div className="flex items-center justify-center space-x-4 text-black">
                        <div className="p-2 border-2 border-black">
                            <FileVideo className="h-8 w-8 sm:h-10 sm:w-10" />
                        </div>
                        <span className="font-bold text-lg sm:text-xl truncate max-w-xs uppercase">{file.name}</span>
                    </div>
                    <div className="text-sm font-bold text-gray-500 uppercase">
                        {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </div>

                    {uploading && (
                        <div className="w-full bg-gray-200 h-4 border-2 border-black">
                            <div className="bg-black h-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                        </div>
                    )}

                    <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-6">
                        <button
                            onClick={clearFile}
                            disabled={uploading}
                            className="w-full sm:w-auto px-6 py-3 bg-white text-black border-4 border-black font-black uppercase hover:bg-gray-100 transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                        >
                            Change File
                        </button>
                        <button
                            onClick={handleUpload}
                            disabled={uploading}
                            className="w-full sm:w-auto px-6 py-3 bg-black text-white border-4 border-black font-black uppercase hover:bg-white hover:text-black transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                        >
                            {uploading ? `UPLOADING ${progress}%` : 'START UPLOAD'}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UploadBox;
