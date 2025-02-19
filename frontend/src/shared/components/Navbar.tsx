import { Link } from "@tanstack/react-router";
import clsx from "clsx";

interface Props {
	className?: string;
}
export function Navbar({ className }: Props) {
	return (
		<nav
			className={clsx(
				className,
				"flex-col h-screen bg-[#204933] shadow items-center z-max w-32",
			)}
		>
			<img
				alt="Canopée"
				src="src/assets/canopee_icon-blanc-simplifiee-rvb.png"
				className="h-auto w-auto aspect-square object-cover pt-6 px-4"
			/>
			<div className="flex grow">
				{/* <Link
					to="/clear-cuttings/map"
					activeProps={{
						className: "border-green-500  text-gray-900",
					}}
					inactiveProps={{
						className:
							"border-transparent  text-gray-500 hover:border-gray-300 hover:text-gray-700",
					}}
					className="inline-flex items-center border-b-2 h-full px-1 pt-1 text-sm font-medium "
				>
					Coupes rases
				</Link> */}
			</div>
		</nav>
	);
}
