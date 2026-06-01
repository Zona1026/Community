<template>
  <nav class="navbar navbar-expand-lg bg-white border-bottom sticky-top">
    <div class="container-fluid px-4">
      <RouterLink class="navbar-brand fw-bold" to="/">Trend Radar</RouterLink>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#mainNavigation"
        aria-controls="mainNavigation"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div id="mainNavigation" class="collapse navbar-collapse">
        <ul class="navbar-nav ms-auto gap-lg-2">
          <li class="nav-item">
            <RouterLink class="nav-link" to="/">趨勢雷達</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/explore">趨勢探索</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/industries">產業靈感</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/reports">趨勢報告</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="/saved">收藏</RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>
