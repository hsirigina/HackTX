export default function PitStopNotification({ pitStop }) {
  if (!pitStop) return null;

  return (
    <div className="fixed top-4 right-4 bg-orange-600 text-white p-6 rounded-lg shadow-2xl animate-bounce z-50">
      <div className="text-3xl font-bold mb-2">🔧 PIT STOP!</div>
      <div className="text-lg">Lap {pitStop.lap_number}</div>
      <div className="text-lg font-semibold">
        {pitStop.old_compound} → {pitStop.new_compound}
      </div>
      <div className="text-sm mt-2 opacity-90">
        Time loss: {pitStop.pit_duration_seconds}s
      </div>
    </div>
  );
}
