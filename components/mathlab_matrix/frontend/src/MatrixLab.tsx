import { useEffect, useMemo, useState, useCallback } from "react"
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib"

type Matrix = number[][]

/* ---------- Utilitaires d'algèbre linéaire ---------- */

function identity(n: number): Matrix {
  return Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))
  )
}

function transpose(m: Matrix): Matrix {
  return m[0].map((_, j) => m.map(row => row[j]))
}

function multiply(a: Matrix, b: Matrix): Matrix {
  const n = a.length
  const p = b[0].length
  const q = b.length
  const out: Matrix = Array.from({ length: n }, () => Array(p).fill(0))
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < p; j++) {
      let s = 0
      for (let k = 0; k < q; k++) s += a[i][k] * b[k][j]
      out[i][j] = s
    }
  }
  return out
}

function power(m: Matrix, k: number): Matrix {
  if (k <= 0) return identity(m.length)
  let result = identity(m.length)
  let base = m.map(r => [...r])
  let exp = k
  while (exp > 0) {
    if (exp & 1) result = multiply(result, base)
    base = multiply(base, base)
    exp = exp >> 1
  }
  return result
}

function determinant(m: Matrix): number {
  const n = m.length
  if (n === 1) return m[0][0]
  if (n === 2) return m[0][0] * m[1][1] - m[0][1] * m[1][0]
  if (n === 3) {
    const [a, b, c] = m[0]
    const [d, e, f] = m[1]
    const [g, h, i] = m[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
  }
  // Fallback général (élimination LU)
  const M = m.map(r => [...r])
  let det = 1
  for (let i = 0; i < n; i++) {
    let pivot = i
    for (let k = i + 1; k < n; k++)
      if (Math.abs(M[k][i]) > Math.abs(M[pivot][i])) pivot = k
    if (pivot !== i) { [M[i], M[pivot]] = [M[pivot], M[i]]; det = -det }
    if (Math.abs(M[i][i]) < 1e-12) return 0
    det *= M[i][i]
    for (let k = i + 1; k < n; k++) {
      const factor = M[k][i] / M[i][i]
      for (let j = i; j < n; j++) M[k][j] -= factor * M[i][j]
    }
  }
  return det
}

function inverse(m: Matrix): Matrix | null {
  const n = m.length
  const det = determinant(m)
  if (Math.abs(det) < 1e-12) return null
  // Élimination Gauss-Jordan sur [M | I]
  const A = m.map((row, i) => [...row, ...identity(n)[i]])
  for (let i = 0; i < n; i++) {
    let pivot = i
    for (let k = i + 1; k < n; k++)
      if (Math.abs(A[k][i]) > Math.abs(A[pivot][i])) pivot = k
    if (pivot !== i) [A[i], A[pivot]] = [A[pivot], A[i]]
    const p = A[i][i]
    for (let j = 0; j < 2 * n; j++) A[i][j] /= p
    for (let k = 0; k < n; k++) {
      if (k === i) continue
      const factor = A[k][i]
      for (let j = 0; j < 2 * n; j++) A[k][j] -= factor * A[i][j]
    }
  }
  return A.map(row => row.slice(n))
}

function rank(m: Matrix): number {
  const M = m.map(r => [...r])
  const rows = M.length
  const cols = M[0].length
  let r = 0
  for (let c = 0; c < cols && r < rows; c++) {
    let pivot = r
    for (let i = r + 1; i < rows; i++)
      if (Math.abs(M[i][c]) > Math.abs(M[pivot][c])) pivot = i
    if (Math.abs(M[pivot][c]) < 1e-10) continue
    [M[r], M[pivot]] = [M[pivot], M[r]]
    for (let i = r + 1; i < rows; i++) {
      const factor = M[i][c] / M[r][c]
      for (let j = c; j < cols; j++) M[i][j] -= factor * M[r][j]
    }
    r++
  }
  return r
}

function trace(m: Matrix): number {
  return m.reduce((s, row, i) => s + row[i], 0)
}

function fmt(x: number): string {
  if (!Number.isFinite(x)) return "—"
  if (Math.abs(x) < 1e-9) return "0"
  if (Math.abs(x) >= 1e6 || Math.abs(x) < 1e-3) return x.toExponential(2)
  return (Math.round(x * 1000) / 1000).toString()
}

/* ---------- Composant ---------- */

function MatrixLab({ args }: ComponentProps) {
  const initial: Matrix = args.initial_matrix ?? identity(3)
  const initialSize: number = args.size ?? initial.length

  const [size, setSize] = useState<number>(initialSize)
  const [matrix, setMatrix] = useState<Matrix>(initial)
  const [k, setK] = useState<number>(2)

  /* Mode clair verrouillé — on force le stamp light quel que soit le thème
     Streamlit ou système. */
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", "light")
  }, [])

  useEffect(() => {
    Streamlit.setFrameHeight()
  })

  const det = useMemo(() => determinant(matrix), [matrix])
  const tr = useMemo(() => trace(matrix), [matrix])
  const rk = useMemo(() => rank(matrix), [matrix])
  const inv = useMemo(() => inverse(matrix), [matrix])
  const trans = useMemo(() => transpose(matrix), [matrix])
  const pw = useMemo(() => power(matrix, k), [matrix, k])

  /* Envoi à Streamlit chaque fois que la matrice ou k change */
  useEffect(() => {
    Streamlit.setComponentValue({
      matrix,
      determinant: det,
      trace: tr,
      rank: rk,
      power_k: k,
      power_result: pw,
      inverse: inv,
      transpose: trans,
    })
  }, [matrix, k, det, tr, rk, inv, trans, pw])

  const updateCell = useCallback((i: number, j: number, v: string) => {
    const num = parseFloat(v)
    if (isNaN(num)) return
    setMatrix(prev => {
      const next = prev.map(r => [...r])
      next[i][j] = num
      return next
    })
  }, [])

  const changeSize = (n: number) => {
    setSize(n)
    setMatrix(identity(n))
  }

  const preset = (kind: "identity" | "random" | "fib" | "rotation") => {
    if (kind === "identity") setMatrix(identity(size))
    else if (kind === "random") {
      setMatrix(Array.from({ length: size }, () =>
        Array.from({ length: size }, () => Math.round((Math.random() * 6 - 3) * 10) / 10)
      ))
    }
    else if (kind === "fib" && size === 2) {
      setMatrix([[1, 1], [1, 0]])
    }
    else if (kind === "rotation") {
      const t = Math.PI / 6
      const c = Math.cos(t), s = Math.sin(t)
      if (size === 2) setMatrix([[c, -s], [s, c]])
      else setMatrix([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    }
  }

  const singular = inv === null

  return (
    <div className="matrixlab">
      <div className="eyebrow">MathLab · Module Matrices — Démo React</div>
      <h2>Algèbre linéaire, en direct</h2>
      <p className="sub">
        Saisissez les coefficients — déterminant, rang, trace, transposée, inverse
        et puissances se recalculent instantanément côté client, en TypeScript pur.
      </p>

      <div className="wrap">
        <div>
          <div
            className="matrix-grid"
            style={{ gridTemplateColumns: `repeat(${size}, auto)` }}
          >
            {matrix.map((row, i) =>
              row.map((v, j) => (
                <input
                  key={`${i}-${j}`}
                  type="number"
                  step="0.1"
                  value={v}
                  onChange={e => updateCell(i, j, e.target.value)}
                />
              ))
            )}
          </div>

          <div className="controls">
            <button
              className={`chip ${size === 2 ? "active" : ""}`}
              onClick={() => changeSize(2)}
            >2×2</button>
            <button
              className={`chip ${size === 3 ? "active" : ""}`}
              onClick={() => changeSize(3)}
            >3×3</button>
          </div>
          <div className="controls">
            <button className="chip" onClick={() => preset("identity")}>Identité</button>
            <button className="chip" onClick={() => preset("random")}>Aléatoire</button>
            {size === 2 && (
              <button className="chip" onClick={() => preset("fib")}>Fibonacci</button>
            )}
            <button className="chip" onClick={() => preset("rotation")}>Rotation 30°</button>
          </div>
        </div>

        <div className="results">
          <div className="kpi-row">
            <div className="kpi">
              <div className="label">Déterminant</div>
              <div className={`value ${singular ? "warn" : "good"}`}>{fmt(det)}</div>
            </div>
            <div className="kpi">
              <div className="label">Trace</div>
              <div className="value">{fmt(tr)}</div>
            </div>
            <div className="kpi">
              <div className="label">Rang</div>
              <div className="value">{rk}</div>
            </div>
          </div>

          <div className="result-matrix">
            <div className="head">
              <h3>Puissance M<sup>k</sup></h3>
              <span className="badge">k = {k}</span>
            </div>
            <div className="power-control">
              <input
                type="range" min={0} max={15} value={k}
                onChange={e => setK(parseInt(e.target.value))}
              />
              <span className="k-value">{k}</span>
            </div>
            <div
              className="grid"
              style={{ gridTemplateColumns: `repeat(${size}, 1fr)`, marginTop: 10 }}
            >
              {pw.flat().map((v, i) => (
                <div key={i} className="cell">{fmt(v)}</div>
              ))}
            </div>
          </div>

          <div className="result-matrix">
            <div className="head">
              <h3>Transposée M<sup>T</sup></h3>
              <span className="badge">échange lignes/colonnes</span>
            </div>
            <div className="grid" style={{ gridTemplateColumns: `repeat(${size}, 1fr)` }}>
              {trans.flat().map((v, i) => (
                <div key={i} className="cell">{fmt(v)}</div>
              ))}
            </div>
          </div>

          <div className="result-matrix">
            <div className="head">
              <h3>Inverse M<sup>-1</sup></h3>
              <span className="badge">Gauss-Jordan</span>
            </div>
            {singular ? (
              <div className="singular-note">
                Matrice singulière — déterminant nul, pas d'inverse.
              </div>
            ) : (
              <div className="grid" style={{ gridTemplateColumns: `repeat(${size}, 1fr)` }}>
                {inv!.flat().map((v, i) => (
                  <div key={i} className="cell">{fmt(v)}</div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default withStreamlitConnection(MatrixLab)
