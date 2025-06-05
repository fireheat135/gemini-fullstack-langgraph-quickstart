import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

// TDD: Red Phase - 失敗するテストを先に書く
describe('テスト環境の検証', () => {
  it('基本的なテストが動作する', () => {
    expect(1 + 1).toBe(2)
  })

  it('React Testing Libraryが正しく動作する', () => {
    render(<div data-testid="test-element">テスト</div>)
    const element = screen.getByTestId('test-element')
    expect(element).toBeInTheDocument()
    expect(element).toHaveTextContent('テスト')
  })
})