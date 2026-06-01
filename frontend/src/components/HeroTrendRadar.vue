<template>
  <section class="py-5 border-bottom bg-light">
    <div class="container-fluid px-4">
      <div class="row align-items-center g-4">
        <div class="col-lg-7">
          <span class="badge text-bg-dark mb-3">Trend Radar</span>
          <h1 class="display-5 fw-bold mb-3">發現正在升溫的內容趨勢</h1>
          <p class="lead text-secondary mb-4">
            即時追蹤社群、新聞與網路討論，找出值得跟進的話題、梗與內容靈感。
          </p>
          <div class="d-flex flex-wrap gap-2">
            <a class="btn btn-primary btn-lg" href="#today-trends">查看今日趨勢</a>
            <RouterLink class="btn btn-outline-dark btn-lg" to="/industries">
              輸入產業找靈感
            </RouterLink>
          </div>
        </div>

        <div class="col-lg-5">
          <div class="border rounded-3 bg-white p-4 shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span class="fw-semibold">今日雷達訊號</span>
              <span class="badge text-bg-success">Live Mock</span>
            </div>
            <div class="row g-3">
              <div class="col-6">
                <div class="border rounded-2 p-3">
                  <div class="fs-3 fw-bold">5</div>
                  <div class="text-secondary small">觀察趨勢</div>
                </div>
              </div>
              <div class="col-6">
                <div class="border rounded-2 p-3">
                  <div class="fs-3 fw-bold">3</div>
                  <div class="text-secondary small">升溫訊號</div>
                </div>
              </div>
              <div class="col-6">
                <div class="border rounded-2 p-3">
                  <div class="fs-3 fw-bold">4</div>
                  <div class="text-secondary small">涵蓋平台</div>
                </div>
              </div>
              <div class="col-6">
                <div class="border rounded-2 p-3">
                  <div class="fs-3 fw-bold">2</div>
                  <div class="text-secondary small">高風險議題</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
