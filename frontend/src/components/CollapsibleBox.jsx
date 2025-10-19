import { useState } from 'react'

export default function CollapsibleBox({ title, icon, defaultOpen = false, children }) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="bg-gray-800 bg-opacity-70 rounded-lg shadow-2xl border border-gray-700 overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-colors flex items-center justify-between"
      >
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{icon}</span>
          <h2 className="text-xl font-bold text-white">{title}</h2>
        </div>
        <span className="text-white text-2xl">
          {isOpen ? '▼' : '▶'}
        </span>
      </button>

      {isOpen && (
        <div className="p-4">
          {children}
        </div>
      )}
    </div>
  )
}
