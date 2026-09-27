import { useCallback, useEffect, useState } from "react";

/** Runs an async loader on mount / when deps change. Returns { data, loading, error, reload, setData }. */
export function useLoad(loader, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: "" });

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const run = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: "" }));
    try {
      const data = await loader();
      setState({ data, loading: false, error: "" });
    } catch (e) {
      setState({ data: null, loading: false, error: e.message });
    }
  }, deps);

  useEffect(() => {
    run();
  }, [run]);

  const setData = (d) => setState((s) => ({ ...s, data: typeof d === "function" ? d(s.data) : d }));
  return { ...state, reload: run, setData };
}

/** Treat 404 as "nothing yet" instead of an error. */
export const orNull = (promise) => promise.catch((e) => (e.status === 404 ? null : Promise.reject(e)));
