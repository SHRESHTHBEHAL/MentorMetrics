export interface Transcript {
    id: string;
    session_id: string;
    raw_text: string | null;
    segments: Segment[] | null;
    word_timestamps: any[] | null;
    created_at: string;
    updated_at: string;
}

export interface Segment {
    start: number;
    end: number;
    text: string;
    confidence?: number;
}
