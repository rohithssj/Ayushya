import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  const baseDir = process.cwd();
  
  // Lightweight check for production retrieval index files
  const metadataPath = path.join(baseDir, 'data', 'embeddings', 'legal_chunks', 'metadata.json');
  const vectorsPath = path.join(baseDir, 'data', 'embeddings', 'legal_chunks', 'vectors.npy');
  const processedDir = path.join(baseDir, 'data', 'processed');

  const indexExists = fs.existsSync(metadataPath) && fs.existsSync(vectorsPath);
  const processedChunksExist = fs.existsSync(processedDir) && fs.readdirSync(processedDir).length > 0;

  const isReady = indexExists && processedChunksExist;

  return NextResponse.json(
    {
      status: isReady ? 'ok' : 'degraded',
      service: 'ayushya-rag',
      timestamp: new Date().toISOString(),
      checks: {
        retrieval_index: indexExists ? 'loaded' : 'missing',
        processed_chunks: processedChunksExist ? 'available' : 'missing',
      },
    },
    { status: isReady ? 200 : 503 }
  );
}
