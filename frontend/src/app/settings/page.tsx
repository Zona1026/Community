import Link from 'next/link';
import { UserSettingsForm } from '../../components/UserSettingsForm';

export default function SettingsPage() {
  return (
    <main className="page">
      <div className="page__inner">
        <header className="page__header">
          <p className="page__eyebrow">User Settings</p>
          <h1>使用者設定</h1>
          <p className="page__description">
            儲存 Demo 會用到的產業類別、常用語氣與自訂關鍵字。沒有資料庫時會先使用前端 fallback。
          </p>
          <Link className="page__link" href="/">
            回到 Dashboard
          </Link>
        </header>

        <section className="settings-panel" aria-label="使用者設定表單">
          <UserSettingsForm />
        </section>
      </div>
    </main>
  );
}
