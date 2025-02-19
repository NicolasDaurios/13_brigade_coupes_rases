import { ClearCuttings } from "@/features/clear-cutting/components/map/ClearCuttings";
import { useGeolocation } from "@/shared/hooks/geolocation";
import type { LatLngExpression } from "leaflet";
import { MapContainer, TileLayer } from "react-leaflet";
import { useMapInstance } from "./Map.context";
import { useEffect, useRef, useState } from "react";
import { Outlet, useNavigate } from "@tanstack/react-router";

const franceCenter: LatLngExpression = [46.695554, 2.440236];
const wholeFranceZoom = 7;

export function InteractiveMap() {
	const { browserLocation } = useGeolocation();
	console.log(browserLocation);

	const { setMap } = useMapInstance();

	const navigate = useNavigate();

	// Cette action sera effectuée une fois que le composant est monté
	useEffect(() => {
		// Exemple: Rediriger immédiatement vers une sous-page
		navigate({ to: "/map/list", replace: false });
	}, [navigate]);

	return (
		<>
			<main className="h-screen w-full">
				<MapContainer
					className="h-full"
					center={franceCenter}
					zoom={wholeFranceZoom}
					scrollWheelZoom={true}
					ref={setMap}
				>
					<TileLayer
						attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
						url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
					/>
					<ClearCuttings />
				</MapContainer>
			</main>

			<div className="hidden right-0 lg:inset-y-0 lg:z-50 lg:flex lg:w-200 lg:flex-col px-8">
				<Outlet />
			</div>
		</>
	);
}
