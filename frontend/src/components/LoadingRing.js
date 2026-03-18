export default function LoadingRing({ size = "medium" }) {
  return <span className={`loading-ring loading-ring--${size}`} aria-hidden="true" />;
}
