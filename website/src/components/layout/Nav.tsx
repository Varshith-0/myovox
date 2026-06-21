import { NavLink } from 'react-router-dom'
import { NAV_LINKS, SITE } from '@/data/site'
import { LogoMark } from '@/components/ui/LogoMark'
import styles from './Nav.module.css'

/** Fixed, minimal top navigation present on every page. */
export function Nav() {
  return (
    <header className={styles.nav}>
      <NavLink to="/" className={styles.brand} aria-label={`${SITE.title} — home`}>
        <LogoMark className={styles.mark} size={24} duration={12} />
        <span className={styles.wordmark}>{SITE.brand}</span>
      </NavLink>

      <nav className={styles.links} aria-label="Primary">
        {NAV_LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => (isActive ? `${styles.link} ${styles.active}` : styles.link)}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
