import clsx from 'clsx';

interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  labelOn?: string;
  labelOff?: string;
}

export default function ToggleSwitch({
  checked,
  onChange,
  disabled = false,
  labelOn = 'ON',
  labelOff = 'OFF',
}: ToggleSwitchProps) {
  return (
    <div className="flex items-center gap-3">
      <span
        className={clsx(
          'text-xs font-mono transition-colors',
          !checked ? 'text-accent-blue font-bold' : 'text-dark-400',
        )}
      >
        {labelOff}
      </span>

      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={clsx(
          'relative inline-flex h-7 w-14 items-center rounded-full transition-colors duration-300',
          checked
            ? 'bg-gradient-to-r from-accent-purple to-accent-green'
            : 'bg-dark-600',
          disabled && 'opacity-50 cursor-not-allowed',
        )}
      >
        <span
          className={clsx(
            'inline-block h-5 w-5 transform rounded-full bg-white transition-transform duration-300 shadow-md',
            checked ? 'translate-x-8' : 'translate-x-1',
          )}
        />
      </button>

      <span
        className={clsx(
          'text-xs font-mono transition-colors',
          checked ? 'text-accent-green font-bold' : 'text-dark-400',
        )}
      >
        {labelOn}
      </span>
    </div>
  );
}
