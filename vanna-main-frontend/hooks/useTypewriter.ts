/**
 * Typewriter Hook
 * Provides typewriter effect for text display
 */

import { useState, useEffect } from 'react';

export interface UseTypewriterOptions {
  text: string;
  speed?: number; // milliseconds per character
  enabled?: boolean; // enable/disable effect
}

export interface UseTypewriterReturn {
  displayText: string;
  isTyping: boolean;
}

export function useTypewriter({
  text,
  speed = 60,
  enabled = true,
}: UseTypewriterOptions): UseTypewriterReturn {
  const [displayText, setDisplayText] = useState(enabled ? '' : text);
  const [isTyping, setIsTyping] = useState(enabled);

  useEffect(() => {
    // Eğer efekt kapalıysa, tüm metni direkt göster
    if (!enabled) {
      setDisplayText(text);
      setIsTyping(false);
      return;
    }

    // Reset when text changes
    setDisplayText('');
    setIsTyping(true);

    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < text.length) {
        currentIndex++;
        setDisplayText(text.slice(0, currentIndex));
      } else {
        setIsTyping(false);
        clearInterval(interval);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed, enabled]);

  return { displayText, isTyping };
}
