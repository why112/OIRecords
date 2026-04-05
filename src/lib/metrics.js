const STATUS_TEXT = {
  solved: '已完成',
  attempted: '尝试中',
  unsolved: '未开始'
};

export function formatProgress(solved, total) {
  return `${solved} / ${total}`;
}

export function getCompletionPercent(solved, total) {
  if (!total) {
    return 0;
  }

  return (solved / total) * 100;
}

export function getProgressTone(solved, total) {
  const percent = getCompletionPercent(solved, total);

  if (percent === 0) {
    return 'slate';
  }

  if (percent <= 30) {
    return 'red';
  }

  if (percent <= 60) {
    return 'orange';
  }

  if (percent < 100) {
    return 'yellow';
  }

  return 'green';
}

export function getProblemTone(status) {
  if (status === 'solved') {
    return 'green';
  }

  if (status === 'attempted') {
    return 'red';
  }

  return 'slate';
}

export function getProblemStatusText(status) {
  return STATUS_TEXT[status] || STATUS_TEXT.unsolved;
}

