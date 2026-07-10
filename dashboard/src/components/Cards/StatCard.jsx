// src/components/Cards/StatCard.jsx
const StatCard = ({ label, value, color, icon }) => {
  const colors = {
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    red: 'bg-red-50 text-red-700 border-red-200',
    gray: 'bg-gray-50 text-gray-700 border-gray-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
  };

  return (
    <div className={`p-4 rounded-xl border ${colors[color] || colors.blue} transition-all hover:shadow-md`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="text-3xl opacity-80">{icon}</div>
      </div>
    </div>
  );
};

export default StatCard;