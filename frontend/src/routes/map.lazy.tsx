import { InteractiveMap } from '@/features/clear-cutting/components/map/InteractiveMap'
import { createLazyFileRoute } from '@tanstack/react-router'

export const Route = createLazyFileRoute('/map')({
  component: InteractiveMap,
})
