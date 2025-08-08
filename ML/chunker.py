import re

def main_chunk_function(text, chunk_type="balanced"):
    """
    Universal document chunker - works with any document format.
    
    Args:
        text: Raw document text string (PDF, Word, etc.)
        chunk_type: "balanced" (default), "semantic", or "sliding_window"
    
    Returns:
        List of text chunks ready for vector embedding
    """
    if chunk_type == "semantic":
        return semantic_chunk_text(text)
    elif chunk_type == "sliding_window":
        return sliding_window_chunk(text)
    else:
        return balanced_chunk_text(text)

def balanced_chunk_text(text, min_chunk_size=250, max_chunk_size=800, overlap_size=100):
    """
    General-purpose chunker that works with any document type.
    Balances chunk size with semantic boundaries.
    """
    # Basic text cleaning
    text = clean_text(text)
    
    # Split into sentences for better boundary detection
    sentences = split_into_sentences(text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Check if adding this sentence exceeds max size
        potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
        
        if len(potential_chunk.strip()) > max_chunk_size:
            # If current chunk meets minimum size, save it
            if len(current_chunk.strip()) >= min_chunk_size:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                overlap = get_sentence_overlap(current_chunk, overlap_size)
                current_chunk = overlap + " " + sentence if overlap else sentence
            else:
                # Current chunk too small, just add the sentence
                current_chunk = potential_chunk
        else:
            current_chunk = potential_chunk
    
    # Add final chunk if it meets minimum size
    if current_chunk.strip() and len(current_chunk.strip()) >= min_chunk_size:
        chunks.append(current_chunk.strip())
    
    # Merge any remaining small chunks
    return merge_small_chunks(chunks, min_chunk_size)

def semantic_chunk_text(text, target_size=500, size_tolerance=0.3):
    """
    Semantic chunking based on natural document structure.
    Works with paragraphs, sections, and natural breaks.
    """
    text = clean_text(text)
    
    # Try to identify natural breaks in order of preference
    chunks = []
    
    # First, try double line breaks (paragraphs)
    if '\n\n' in text:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = group_by_size(paragraphs, target_size, size_tolerance)
    
    # If no clear paragraphs, try single line breaks
    elif '\n' in text:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        chunks = group_by_size(lines, target_size, size_tolerance)
    
    # Fall back to sentence-based chunking
    else:
        sentences = split_into_sentences(text)
        chunks = group_by_size(sentences, target_size, size_tolerance)
    
    return chunks

def sliding_window_chunk(text, window_size=600, overlap_size=150):
    """
    Sliding window approach - creates overlapping chunks of fixed size.
    Good for ensuring no information is lost at boundaries.
    """
    text = clean_text(text).replace('\n', ' ')
    
    if len(text) <= window_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + window_size
        chunk = text[start:end]
        
        # Try to end at a sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            last_space = chunk.rfind(' ')
            
            if last_period > len(chunk) * 0.8:  # Period in last 20%
                chunk = text[start:start + last_period + 1]
            elif last_space > len(chunk) * 0.8:  # Space in last 20%
                chunk = text[start:start + last_space]
        
        chunks.append(chunk.strip())
        
        if end >= len(text):
            break
            
        start = end - overlap_size
    
    return [chunk for chunk in chunks if len(chunk.strip()) > 50]

def clean_text(text):
    """Clean and normalize text from any document type."""
    if not text:
        return ""
    
    # Remove excessive whitespace while preserving structure
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 consecutive newlines
    text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces
    text = re.sub(r'\r\n', '\n', text)  # Normalize line endings
    
    # Remove page numbers, headers, footers (common patterns)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)  # Standalone numbers
    text = re.sub(r'\n\s*Page \d+.*?\n', '\n', text, flags=re.IGNORECASE)
    
    return text.strip()

def split_into_sentences(text):
    """Split text into sentences using multiple delimiters."""
    # Handle common sentence endings
    sentence_pattern = r'[.!?]+(?:\s+|$)'
    sentences = re.split(sentence_pattern, text)
    
    # Clean and filter sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Rejoin sentences that might have been split incorrectly
    cleaned_sentences = []
    for i, sentence in enumerate(sentences):
        if sentence:
            # Add back the punctuation (except for last sentence)
            if i < len(sentences) - 1 and not sentence.endswith(('.', '!', '?')):
                # Try to determine original punctuation
                original_end = text.find(sentence) + len(sentence)
                if original_end < len(text) and text[original_end] in '.!?':
                    sentence += text[original_end]
            cleaned_sentences.append(sentence)
    
    return cleaned_sentences

def group_by_size(text_units, target_size, tolerance=0.3):
    """Group text units (paragraphs, sentences) into appropriately sized chunks."""
    chunks = []
    current_chunk = ""
    
    for unit in text_units:
        potential_chunk = current_chunk + "\n\n" + unit if current_chunk else unit
        
        # If within acceptable size range, continue building chunk
        if len(potential_chunk) <= target_size * (1 + tolerance):
            current_chunk = potential_chunk
        else:
            # Current chunk is good size, start new one
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = unit
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def get_sentence_overlap(text, overlap_size):
    """Get overlap text preferring complete sentences."""
    if len(text) <= overlap_size:
        return text
    
    # Find sentence boundaries in the overlap region
    overlap_start = max(0, len(text) - overlap_size)
    overlap_text = text[overlap_start:]
    
    # Look for sentence start (capital letter after punctuation and space)
    sentence_start = re.search(r'[.!?]\s+[A-Z]', overlap_text)
    
    if sentence_start:
        return overlap_text[sentence_start.start() + 2:]  # Skip punctuation and space
    else:
        return overlap_text

def merge_small_chunks(chunks, min_size):
    """Merge chunks that are too small with their neighbors."""
    if not chunks:
        return chunks
        
    merged = []
    i = 0
    
    while i < len(chunks):
        current = chunks[i]
        
        # If current chunk is too small, try to merge
        if len(current) < min_size:
            if i + 1 < len(chunks):  # Merge with next
                merged.append(current + "\n\n" + chunks[i + 1])
                i += 2
            elif merged:  # Merge with previous
                merged[-1] = merged[-1] + "\n\n" + current
                i += 1
            else:  # Keep as is if it's the only chunk
                merged.append(current)
                i += 1
        else:
            merged.append(current)
            i += 1
    
    return merged

# Utility function for performance testing
def analyze_chunks(chunks):
    """Analyze chunk statistics for optimization."""
    if not chunks:
        return {}
    
    lengths = [len(chunk) for chunk in chunks]
    return {
        'total_chunks': len(chunks),
        'avg_length': sum(lengths) / len(lengths),
        'min_length': min(lengths),
        'max_length': max(lengths),
        'total_characters': sum(lengths)
    }