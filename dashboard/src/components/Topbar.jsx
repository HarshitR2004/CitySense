import React, { useState, useEffect } from 'react';
import { Calendar } from 'lucide-react';

export function Topbar() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formattedDate = currentTime.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const formattedTime = currentTime.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="fixed top-0 left-80 right-0 h-16 bg-black border-b-2 border-white/20 flex items-center justify-center px-8 z-40">
      <div className="flex items-center justify-center w-full">
        {/* Date & Time */}
        <div className="hidden lg:flex flex-col items-center text-sm font-mono">
          <div className="flex items-center gap-2 text-white/70">
            <Calendar size={16} />
            <span className="uppercase">{formattedDate}</span>
          </div>
          <span className="text-xs text-acid mt-1 font-bold">{formattedTime}</span>
        </div>        

      </div>
    </div>
  );
}
