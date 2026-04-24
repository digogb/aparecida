import { useMediaQuery } from './useMediaQuery'

/** True when viewport is below the `md` breakpoint (768px). */
export function useIsMobile(): boolean {
  return useMediaQuery('(max-width: 767px)')
}
