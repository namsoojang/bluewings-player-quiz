/** GitHub Pages의 저장소 하위 경로와 로컬 실행을 모두 지원합니다. */
export function assetPath(path: string) { return `${import.meta.env.BASE_URL}${path.replace(/^\//, '')}`; }
