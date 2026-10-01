/** Polyfills mínimos para componentes que usan APIs del navegador en tests. */

if (typeof window !== 'undefined') {
  if (typeof window.IntersectionObserver === 'undefined') {
    class IntersectionObserverStub implements IntersectionObserver {
      readonly root: Element | Document | null = null;
      readonly rootMargin: string = '';
      readonly thresholds: ReadonlyArray<number> = [];
      observe(): void {
        // sin lado observable en tests
      }
      unobserve(): void {
        // sin lado observable en tests
      }
      disconnect(): void {
        // sin lado observable en tests
      }
      takeRecords(): IntersectionObserverEntry[] {
        return [];
      }
    }
    window.IntersectionObserver = IntersectionObserverStub;
  }

  if (typeof window.matchMedia !== 'function') {
    window.matchMedia = (query: string): MediaQueryList =>
      ({
        matches: false,
        media: query,
        onchange: null,
        addListener: () => undefined,
        removeListener: () => undefined,
        addEventListener: () => undefined,
        removeEventListener: () => undefined,
        dispatchEvent: () => false,
      }) as unknown as MediaQueryList;
  }
}
