export function shortId(id: string | number, maxSize: number = 8) {
  if (typeof id === 'string') {
    return id.slice(-maxSize);
  } else {
    return id;
  }
}
