/**
 * Utility function to intelligently truncate long AI responses
 */

export function truncateResponse(text: string, maxLength: number = 4500): string {
    if (text.length <= maxLength) {
        return text;
    }

    // Try to find a good breaking point near the max length
    const truncated = text.substring(0, maxLength);

    // Look for sentence endings (., !, ?) in the last 500 characters
    const last500 = truncated.substring(Math.max(0, truncated.length - 500));
    const sentenceEndings = ['.', '!', '?', '\n\n'];

    let bestBreakPoint = truncated.length;

    for (const ending of sentenceEndings) {
        const lastIndex = last500.lastIndexOf(ending);
        if (lastIndex !== -1) {
            const globalIndex = truncated.length - 500 + lastIndex + ending.length;
            if (globalIndex <= maxLength && globalIndex > bestBreakPoint - 200) {
                bestBreakPoint = globalIndex;
            }
        }
    }

    // If we found a good break point, use it
    if (bestBreakPoint < truncated.length) {
        return text.substring(0, bestBreakPoint) + '\n\n[Response truncated for length]';
    }

    // Otherwise, just truncate at max length
    return truncated + '\n\n[Response truncated for length]';
}

/**
 * Check if a response is too long for the backend
 */
export function isResponseTooLong(text: string, maxLength: number = 4500): boolean {
    return text.length > maxLength;
}

/**
 * Get response length info for debugging
 */
export function getResponseInfo(text: string): {
    length: number;
    isTooLong: boolean;
    estimatedWords: number;
} {
    return {
        length: text.length,
        isTooLong: isResponseTooLong(text),
        estimatedWords: text.split(/\s+/).length
    };
} 