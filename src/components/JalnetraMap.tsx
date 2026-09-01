"use client";

import React, { useEffect, useRef } from "react";
import Map, { Source, Layer, MapRef, NavigationControl } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import { useJalnetraStore } from "../store/useJalnetraStore";

export default function JalnetraMap() {
  const { propagation, routes, mapLayers, timeline } = useJalnetraStore();
  const mapRef = useRef<MapRef>(null);

  const floodGeoJSON = propagation?.flood_polygon || { type: "FeatureCollection", features: [] };
  const routeGeoJSON = routes?.safe_departure?.recommended_route?.geometry || {
    type: "FeatureCollection",
    features: []
  };

  // Simulate timeline expansion by increasing opacity based on timeline
  const floodOpacity = timeline === 0 ? 0.3 : Math.min(0.8, 0.3 + (timeline / 100));

  return (
    <div className="absolute inset-0 w-full h-full">
      <Map
        ref={mapRef}
        initialViewState={{
          longitude: 78.078,
          latitude: 30.448,
          zoom: 13,
          pitch: 45,
        }}
        mapStyle={{
          version: 8,
          sources: {
            "osm": {
              type: "raster",
              tiles: ["https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"],
              tileSize: 256,
            }
          },
          layers: [
            {
              id: "osm",
              type: "raster",
              source: "osm",
              minzoom: 0,
              maxzoom: 22,
            }
          ]
        }}
        interactive={true}
      >
        <NavigationControl position="bottom-right" />

        {mapLayers.flood && floodGeoJSON && (
          <Source id="flood" type="geojson" data={floodGeoJSON}>
            <Layer
              id="flood-layer"
              type="fill"
              paint={{
                "fill-color": "#006591",
                "fill-opacity": floodOpacity,
              }}
            />
            <Layer
              id="flood-outline"
              type="line"
              paint={{
                "line-color": "#004c6e",
                "line-width": 2,
              }}
            />
          </Source>
        )}

        {mapLayers.route && routeGeoJSON && (
          <Source id="route" type="geojson" data={routeGeoJSON}>
            <Layer
              id="route-layer"
              type="line"
              paint={{
                "line-color": "#39b8fd",
                "line-width": 5,
              }}
            />
          </Source>
        )}
      </Map>
    </div>
  );
}
