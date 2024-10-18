const sidebar = document.getElementById('sidebar');
const menuIcon = document.getElementById('menu-icon');
const sidebarHeader = document.getElementById('sidebar-header');
const accountButton = document.getElementById('account-button');
const dropdownContent = document.getElementById('dropdown-content');

const sidebarState = localStorage.getItem('sidebarState');
if (sidebarState === 'collapsed') {
    sidebar.classList.add('collapsed');
}

sidebarHeader.addEventListener('click', function() {
    sidebar.classList.toggle('collapsed');
    localStorage.setItem('sidebarState', sidebar.classList.contains('collapsed') ? 'collapsed' : 'expanded');
});

menuIcon.addEventListener('click', function() {
    sidebar.classList.toggle('collapsed');
    localStorage.setItem('sidebarState', sidebar.classList.contains('collapsed') ? 'collapsed' : 'expanded');
});

accountButton.addEventListener('click', function() {
    dropdownContent.classList.toggle('show');
});
