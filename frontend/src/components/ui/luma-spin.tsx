export function LumaSpin() {
  return (
    <div className="relative aspect-square w-[65px]">
      <span className="animate-loader absolute rounded-[50px] shadow-[inset_0_0_0_3px] shadow-gray-800 dark:shadow-gray-100" />
      <span className="animate-loader absolute rounded-[50px] shadow-[inset_0_0_0_3px] shadow-gray-800 [animation-delay:-1.25s] dark:shadow-gray-100" />
    </div>
  )
}
