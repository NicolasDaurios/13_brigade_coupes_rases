import { AsideList } from '@/features/clear-cutting/components/List'
import { createLazyFileRoute } from '@tanstack/react-router'

export const Route = createLazyFileRoute('/map/list')({
  component: RouteComponent,
})

function RouteComponent() {
  return <AsideList />
}
