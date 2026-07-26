import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface ChatBoxProps {
  placeholder: string
  submitLabel: string
  onSubmit: (text: string) => void
  disabled?: boolean
}

export function ChatBox({ placeholder, submitLabel, onSubmit, disabled }: ChatBoxProps) {
  const [text, setText] = useState('')

  function handleSubmit() {
    if (!text.trim()) return
    onSubmit(text.trim())
    setText('')
  }

  return (
    <div className="grid gap-2">
      <Textarea
        placeholder={placeholder}
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        rows={3}
      />
      <Button onClick={handleSubmit} disabled={disabled || !text.trim()} variant="secondary" className="justify-self-end">
        {submitLabel}
      </Button>
    </div>
  )
}
