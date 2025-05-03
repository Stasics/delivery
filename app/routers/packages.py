@router.put("/packages/{tracking_number}/location")
async def update_package_location(
        tracking_number: str,
        location: str,
        db: AsyncSession = Depends(get_db)
):
    """Обновление местоположения посылки"""
    package = await db.execute(
        select(Package)
        .where(Package.tracking_number == tracking_number)
    )
    package = package.scalars().first()

    if not package:
        raise HTTPException(status_code=404, detail="Посылка не найдена")

    package.current_location = location
    package.updated_at = datetime.utcnow()

    db.add(package)
    await db.commit()
    return {"status": "Местоположение обновлено"}


@router.get("/packages/{tracking_number}")
async def track_package(
        tracking_number: str,
        db: AsyncSession = Depends(get_db)
):
    """Получение текущего местоположения посылки"""
    package = await db.execute(
        select(Package)
        .where(Package.tracking_number == tracking_number)
    )
    package = package.scalars().first()

    if not package:
        raise HTTPException(status_code=404, detail="Посылка не найдена")

    return {
        "tracking_number": package.tracking_number,
        "current_location": package.current_location,
        "status": package.status,
        "last_updated": package.updated_at
    }