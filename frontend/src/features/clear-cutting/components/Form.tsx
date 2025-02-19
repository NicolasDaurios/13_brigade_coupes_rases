import { Button } from "@/components/ui/button"
import { useMapInstance } from "./map/Map.context"
import { useNavigate } from "@tanstack/react-router"

type AsideFormProps = {
    clearCuttingId? : string,
}

export function AsideForm({ clearCuttingId } : AsideFormProps) {
    const { map } = useMapInstance();
    const navigate = useNavigate();

    // useEffect(() => {
    //     if (map) {
    //         map.flyTo(clearCuttingPreview.center, 10, { duration: 1});
    //     }
    // }, [map])

    return (
        <>
            <Button onClick={() => navigate({ to: '/map/list' })}>Close</Button>
            <div>Ceci est la fiche {clearCuttingId}</div>
        </>
    );
}