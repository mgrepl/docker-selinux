# RPM spec file for Docker on Fedora
# Some bits borrowed from the openstack-selinux package

%global selinuxtype	targeted
%global moduletype	services
%global modulenames	docker

# Usage: _format var format
#   Expand 'modulenames' into various formats as needed
#   Format must contain '$x' somewhere to do anything useful
%global _format() export %1=""; for x in %{modulenames}; do %1+=%2; %1+=" "; done;

# Relabel files
%global relabel_files() \
     /sbin/restorecon -R %{_bindir}/docker %{_localstatedir}/run/docker.sock %{_localstatedir}/run/docker.pid %{_sharedstatedir}/docker %{_sysconfdir}/docker %{_localstatedir}/log/docker %{_localstatedir}/log/lxc %{_localstatedir}/lock/lxc %{_usr}/lib/systemd/system/docker.service /root/.docker &> /dev/null || : \


# Version of SELinux we were using
%global selinux_policyver 3.13.1-119.fc23

# Package information
Name:			docker-selinux
Version:		0.1.0
Release:		1%{?dist}
License:		GPLv2
Group:			System Environment/Base
Summary:		SELinux Policies for Docker
BuildArch:		noarch
URL:			https://github.com/fedora-cloud/docker-selinux
Requires(post):		selinux-policy-base >= %{selinux_policyver}, selinux-policy-targeted >= %{selinux_policyver}, policycoreutils, policycoreutils-python lib-selinux-utils
BuildRequires:		selinux-policy selinux-policy-devel

#
# wget -c https://github.ncom/lhh/%{name}/archive/%{version}.tar.gz \
#    -O %{name}-%{version}.tar.gz
#
Source:			%{name}-%{version}.tar.gz

%description
SELinux policy modules for use with Docker

%prep
%setup -q

%build
make SHARE="%{_datadir}" TARGETS="%{modulenames}"

%install

# Install SELinux interfaces
%_format INTERFACES $x.if
install -d %{buildroot}%{_datadir}/selinux/devel/include/%{moduletype}
install -p -m 644 $INTERFACES \
	%{buildroot}%{_datadir}/selinux/devel/include/%{moduletype}

# Install policy modules
%_format MODULES $x.pp.bz2
install -d %{buildroot}%{_datadir}/selinux/packages
install -m 0644 $MODULES \
	%{buildroot}%{_datadir}/selinux/packages

%post
#
# Install all modules in a single transaction
#
%_format MODULES %{_datadir}/selinux/packages/$x.pp.bz2
%{_sbindir}/semodule -n -s %{selinuxtype} -i $MODULES
if %{_sbindir}/selinuxenabled ; then
    %{_sbindir}/load_policy
    %relabel_files
fi


%postun
if [ $1 -eq 0 ]; then
	%{_sbindir}/semodule -n -r %{modulenames} &> /dev/null || :
	if %{_sbindir}/selinuxenabled ; then
		%{_sbindir}/load_policy
		%relabel_files
	fi
fi

%files
%defattr(-,root,root,0755)
%attr(0644,root,root) %{_datadir}/selinux/packages/*.pp.bz2
%attr(0644,root,root) %{_datadir}/selinux/devel/include/%{moduletype}/*.if

%changelog
* Fri Mar 06 2015 Lukas Vrabec <lvrabec@redhat.com> - 0.1.0-1
- First Build
