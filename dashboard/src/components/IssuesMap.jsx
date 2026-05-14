import React, { useEffect, useMemo, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { motion, AnimatePresence } from "framer-motion";

const DEFAULT_CENTER = [77.5946, 12.9716];

function getMarkerColor(urgency) {
  if (urgency?.toLowerCase() === "critical") return "#E0FF00";
  if (urgency?.toLowerCase() === "medium") return "#7B00FF";
  return "#FFFFFF";
}

export function IssuesMap({ issues = [], onMarkerClick }) {
  const [selectedMarker, setSelectedMarker] = useState(null);

  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markerRefs = useRef([]);

  // Fixed filtering
  const validIssues = useMemo(() => {
    return issues.filter((issue) => {
      const lat = parseFloat(issue.latitude);
      const lng = parseFloat(issue.longitude);

      return (
        Number.isFinite(lat) &&
        Number.isFinite(lng) &&
        lat >= -90 &&
        lat <= 90 &&
        lng >= -180 &&
        lng <= 180
      );
    });
  }, [issues]);

  // Initialize map only once
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style:
        "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
      center: DEFAULT_CENTER,
      zoom: 12,
      attributionControl: false,
    });

    map.addControl(
      new maplibregl.NavigationControl({
        showCompass: false,
      }),
      "top-right"
    );

    mapRef.current = map;

    return () => {
      markerRefs.current.forEach((m) => m.remove());

      markerRefs.current = [];

      map.remove();

      mapRef.current = null;
    };
  }, []);

  // Marker rendering
  useEffect(() => {
    const map = mapRef.current;

    if (!map) return;

    const renderMarkers = () => {
      markerRefs.current.forEach((m) => m.remove());

      markerRefs.current = [];

      console.log("ALL ISSUES:", issues);
      console.log("VALID ISSUES:", validIssues);

      const bounds = new maplibregl.LngLatBounds();

      validIssues.forEach((issue) => {
        const lng = parseFloat(issue.longitude);
        const lat = parseFloat(issue.latitude);

        const markerEl = document.createElement("div");

        markerEl.className = "custom-marker";

        markerEl.style.width = "30px";
        markerEl.style.height = "30px";
        markerEl.style.borderRadius = "50%";
        markerEl.style.border = "3px solid black";
        markerEl.style.background = getMarkerColor(issue.urgency);
        markerEl.style.boxShadow =
          "0 3px 8px rgba(0,0,0,0.6)";
        markerEl.style.cursor = "pointer";
        markerEl.style.display = "flex";
        markerEl.style.alignItems = "center";
        markerEl.style.justifyContent = "center";
        markerEl.style.zIndex = "9999";

        const dot = document.createElement("div");

        dot.style.width = "8px";
        dot.style.height = "8px";
        dot.style.background = "#000";
        dot.style.borderRadius = "50%";

        markerEl.appendChild(dot);

        markerEl.onclick = () => {
          setSelectedMarker(issue);
          onMarkerClick?.(issue);
        };

        const popup = new maplibregl.Popup({
          offset: 25,
        }).setHTML(`
            <div style="
              background:black;
              color:white;
              padding:10px;
              font-family:monospace;
              text-transform:uppercase;
            ">
              <strong style="color:#E0FF00">
                ${issue.id}
              </strong>

              <br/><br/>

              Urgency:
              <span style="
                color:${getMarkerColor(issue.urgency)}
              ">
                ${issue.urgency}
              </span>
            </div>
        `);

        const marker = new maplibregl.Marker({
          element: markerEl,
        })
          .setLngLat([lng, lat])
          .setPopup(popup)
          .addTo(map);

        markerRefs.current.push(marker);

        bounds.extend([lng, lat]);
      });

      if (!bounds.isEmpty()) {
        map.fitBounds(bounds, {
          padding: 80,
          duration: 1000,
          maxZoom: 15,
        });
      }
    };

    if (map.isStyleLoaded()) {
      renderMarkers();
    } else {
      map.once("load", renderMarkers);
    }
  }, [validIssues, issues, onMarkerClick]);

  return (
    <div className="relative w-full h-full overflow-hidden">

      <div
        ref={mapContainerRef}
        className="absolute inset-0"
      />

      {/* Legend */}

      <motion.div
        className="
        absolute
        bottom-4
        left-4
        bg-black
        p-4
        border
        border-white
        z-50
        text-xs
        font-mono
        uppercase
      "
      >
        <p className="mb-3 font-bold text-white">
          Urgency
        </p>

        <div className="space-y-2">

          <div className="flex items-center gap-2">
            <div
              className="w-4 h-4"
              style={{
                background: "#E0FF00",
              }}
            />
            <span className="text-white">
              Critical
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div
              className="w-4 h-4"
              style={{
                background: "#7B00FF",
              }}
            />
            <span className="text-white">
              Medium
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div
              className="w-4 h-4 bg-white"
            />
            <span className="text-white">
              Low
            </span>
          </div>

        </div>
      </motion.div>

      {/* Right info card */}

      <AnimatePresence>
        {selectedMarker && (
          <motion.div
            initial={{
              opacity: 0,
              x: 20,
            }}
            animate={{
              opacity: 1,
              x: 0,
            }}
            exit={{
              opacity: 0,
              x: 20,
            }}
            className="
              absolute
              top-4
              right-4
              w-72
              bg-black
              border
              border-white
              p-4
              z-50
              font-mono
              uppercase
              text-xs
            "
          >
            <h3 className="text-[#E0FF00] font-bold mb-2">
              {selectedMarker.id}
            </h3>

            {selectedMarker.image && (
              <img
                src={selectedMarker.image}
                alt=""
                className="
                  w-full
                  h-32
                  object-cover
                  mb-3
                "
              />
            )}

            <div className="flex justify-between">
              <span className="text-gray-400">
                Urgency
              </span>

              <span
                style={{
                  color: getMarkerColor(
                    selectedMarker.urgency
                  ),
                }}
              >
                {selectedMarker.urgency}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
